from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.message import Message
from app.models.user import User

message_bp = Blueprint('message', __name__)

@message_bp.route('/message/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST':
        receiver_username = request.form.get('receiver_username')
        content = request.form.get('content')
        is_anonymous = request.form.get('is_anonymous') == 'true'

        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            flash('Username tidak ditemukan!', 'danger')
            return redirect(url_for('message.send'))

        if receiver.id == current_user.id:
            flash('Tidak bisa kirim pesan ke diri sendiri!', 'warning')
            return redirect(url_for('message.send'))

        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            content=content,
            is_anonymous=is_anonymous
        )
        db.session.add(msg)
        db.session.commit()


        from app.models.chat import Notification
        # Di dalam route send, setelah db.session.commit():
        notif = Notification(
            user_id=receiver.id,
            type='valentine',
            title='💌 Pesan Valentine Baru!',
            message='Kamu mendapat pesan valentine baru!' if is_anonymous else f'Pesan dari {current_user.username}',
            link='/message/send'
        )
        db.session.add(notif)
        db.session.commit()

        # Kirim realtime
        from app import socketio
        socketio.emit('new_notification', {
            'type': 'valentine',
            'title': '💌 Pesan Valentine Baru!',
            'message': 'Kamu mendapat pesan valentine!' if is_anonymous else f'Pesan dari {current_user.username}',
            'link': '/message/send'
        }, room=f'user_{receiver.id}')

        flash('Pesan berhasil dikirim! 💌', 'success')
        return redirect(url_for('message.send'))

    messages = Message.query.filter_by(
        receiver_id=current_user.id
    ).order_by(Message.created_at.desc()).all()

    return render_template('message/send.html', messages=messages)