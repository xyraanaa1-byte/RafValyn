from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from app import db, socketio
from app.models.chat import ChatRoom, ChatMessage
from app.models.user import User
from flask_socketio import join_room, leave_room, emit
from datetime import datetime
from sqlalchemy import or_, and_
import os
from werkzeug.utils import secure_filename
from app.models.chat import ChatRoom, ChatMessage, Notification

chat_bp = Blueprint('chat', __name__)

ALLOWED_FILES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp3', 'ogg', 'wav', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILES

def get_or_create_room(user1_id, user2_id):
    room = ChatRoom.query.filter(
        or_(
            and_(ChatRoom.user1_id == user1_id, ChatRoom.user2_id == user2_id),
            and_(ChatRoom.user1_id == user2_id, ChatRoom.user2_id == user1_id)
        )
    ).first()
    if not room:
        room = ChatRoom(user1_id=user1_id, user2_id=user2_id)
        db.session.add(room)
        db.session.commit()
    return room

@chat_bp.route('/chat')
@login_required
def index():
    rooms = ChatRoom.query.filter(
        or_(ChatRoom.user1_id == current_user.id, ChatRoom.user2_id == current_user.id)
    ).order_by(ChatRoom.last_message_at.desc()).all()
    return render_template('chat/index.html', rooms=rooms)

@chat_bp.route('/chat/<int:user_id>')
@login_required
def room(user_id):
    other_user = User.query.get_or_404(user_id)
    chat_room = get_or_create_room(current_user.id, user_id)
    ChatMessage.query.filter_by(room_id=chat_room.id, is_read=False).filter(
        ChatMessage.sender_id != current_user.id
    ).update({'is_read': True})
    db.session.commit()
    return render_template('chat/room.html', room=chat_room, other_user=other_user)

@chat_bp.route('/chat/search')
@login_required
def search_user():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    users = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.id != current_user.id
    ).limit(5).all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@chat_bp.route('/chat/unread')
@login_required
def unread_count():
    rooms = ChatRoom.query.filter(
        or_(ChatRoom.user1_id == current_user.id, ChatRoom.user2_id == current_user.id)
    ).all()
    count = sum(
        ChatMessage.query.filter_by(room_id=r.id, is_read=False).filter(
            ChatMessage.sender_id != current_user.id
        ).count() for r in rooms
    )
    return jsonify({'count': count})

@chat_bp.route('/chat/upload/<int:room_id>', methods=['POST'])
@login_required
def upload_file(room_id):
    if 'file' not in request.files:
        return jsonify({'success': False})
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'File tidak didukung'})

    ext = file.filename.rsplit('.', 1)[1].lower()
    msg_type = 'image' if ext in {'png','jpg','jpeg','gif','webp'} else 'audio'
    filename = f"chat_{room_id}_{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}"

    folder = os.path.join('app', 'static', 'uploads', 'chat')
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))

    room = ChatRoom.query.get_or_404(room_id)
    msg = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=filename,
        message_type=msg_type
    )
    room.last_message_at = datetime.utcnow()
    db.session.add(msg)
    db.session.commit()

    socketio.emit('receive_message', {
        'id': msg.id,
        'content': filename,
        'type': msg_type,
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'time': msg.created_at.strftime('%H:%M'),
    }, room=f'room_{room_id}')

    return jsonify({'success': True, 'msg_id': msg.id, 'filename': filename, 'type': msg_type})

@chat_bp.route('/chat/edit/<int:msg_id>', methods=['POST'])
@login_required
def edit_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    if msg.sender_id != current_user.id:
        return jsonify({'success': False})
    new_content = request.json.get('content', '').strip()
    if not new_content:
        return jsonify({'success': False})
    msg.content = new_content
    msg.is_edited = True
    msg.edited_at = datetime.utcnow()
    db.session.commit()
    socketio.emit('message_edited', {
        'msg_id': msg_id,
        'content': new_content
    }, room=f'room_{msg.room_id}')
    return jsonify({'success': True})

@chat_bp.route('/chat/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    delete_type = request.json.get('type', 'me')

    if delete_type == 'all' and msg.sender_id == current_user.id:
        msg.is_deleted_for_all = True
        msg.content = 'Pesan ini telah dihapus'
        msg.message_type = 'deleted'
        db.session.commit()
        socketio.emit('message_deleted', {
            'msg_id': msg_id,
            'type': 'all'
        }, room=f'room_{msg.room_id}')
    elif delete_type == 'me':
        msg.is_deleted_for_me = current_user.id
        db.session.commit()

    return jsonify({'success': True})

# SocketIO events
@socketio.on('join')
def on_join(data):
    join_room(f"room_{data['room_id']}")

@socketio.on('leave')
def on_leave(data):
    leave_room(f"room_{data['room_id']}")

@socketio.on('send_message')
def on_message(data):
    room_id = data['room_id']
    content = data['content'].strip()
    reply_to_id = data.get('reply_to_id')
    if not content:
        return

    room = ChatRoom.query.get(room_id)
    if not room:
        return

    msg = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        content=content,
        message_type='text',
        reply_to_id=reply_to_id if reply_to_id else None
    )
    room.last_message_at = datetime.utcnow()
    db.session.add(msg)
    db.session.commit()

    # Buat notifikasi untuk penerima
    other_user_id = room.user2_id if room.user1_id == current_user.id else room.user1_id
    notif = Notification(
        user_id=other_user_id,
        type='chat',
        title=f'Pesan dari {current_user.username}',
        message=content[:50] + ('...' if len(content) > 50 else ''),
        link=f'/chat/{current_user.id}'
    )
    db.session.add(notif)
    db.session.commit()

    # Kirim notifikasi realtime
    socketio.emit('new_notification', {
    'type': 'chat',
    'title': f'Pesan dari {current_user.username}',
    'message': content[:50],
    'link': f'/chat/{current_user.id}'
    }, room=f'user_{other_user_id}')

    reply_data = None
    if reply_to_id:
        reply_msg = ChatMessage.query.get(reply_to_id)
        if reply_msg:
            reply_data = {
                'id': reply_msg.id,
                'content': reply_msg.content[:50],
                'sender': reply_msg.sender.username
            }

    emit('receive_message', {
        'id': msg.id,
        'content': content,
        'type': 'text',
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'time': msg.created_at.strftime('%H:%M'),
        'reply': reply_data
    }, room=f'room_{room_id}')

@socketio.on('typing')
def on_typing(data):
    emit('user_typing', {'username': data['username']},
         room=f"room_{data['room_id']}", include_self=False)

@socketio.on('stop_typing')
def on_stop_typing(data):
    emit('user_stop_typing', {}, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('message_read')
def on_read(data):
    emit('messages_read', {}, room=f"room_{data['room_id']}", include_self=False)

    # WebRTC Signaling
@socketio.on('call_offer')
def on_call_offer(data):
    emit('incoming_call', {
        'offer': data['offer'],
        'caller_id': current_user.id,
        'caller_name': current_user.username,
        'call_type': data['call_type'],
        'room_id': data['room_id']
    }, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('call_answer')
def on_call_answer(data):
    emit('call_answered', {
        'answer': data['answer']
    }, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    emit('ice_candidate', {
        'candidate': data['candidate']
    }, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('call_ended')
def on_call_ended(data):
    emit('call_ended', {}, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('call_rejected')
def on_call_rejected(data):
    emit('call_rejected', {}, room=f"room_{data['room_id']}", include_self=False)

@socketio.on('join_user_room')
def on_join_user_room():
    join_room(f'user_{current_user.id}')