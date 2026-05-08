from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models.chat import Notification

notif_bp = Blueprint('notif', __name__)

@notif_bp.route('/notifications')
@login_required
def index():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    return render_template('notifications/index.html', notifications=notifications)

@notif_bp.route('/notifications/count')
@login_required
def count():
    total = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    return jsonify({'count': total})

@notif_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return jsonify({'success': True})

@notif_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})