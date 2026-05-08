from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db, socketio
from app.models.order import Order
from flask_socketio import join_room, emit

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/tracking/<int:order_id>')
@login_required
def track(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return render_template('errors/403.html'), 403
    return render_template('tracking/map.html', order=order)

@tracking_bp.route('/api/tracking/<int:order_id>')
@login_required
def get_location(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'courier_lat': order.courier_lat,
        'courier_lng': order.courier_lng,
        'delivery_lat': order.delivery_lat,
        'delivery_lng': order.delivery_lng,
        'status': order.shipping_status,
        'address': order.delivery_address
    })

@tracking_bp.route('/api/tracking/<int:order_id>/update', methods=['POST'])
@login_required
def update_location(order_id):
    if not current_user.is_admin:
        return jsonify({'success': False})
    order = Order.query.get_or_404(order_id)
    data = request.json
    order.courier_lat = data.get('lat', order.courier_lat)
    order.courier_lng = data.get('lng', order.courier_lng)
    db.session.commit()

    socketio.emit('location_update', {
        'courier_lat': order.courier_lat,
        'courier_lng': order.courier_lng,
        'status': order.shipping_status
    }, room=f'tracking_{order_id}')

    return jsonify({'success': True})

@socketio.on('join_tracking')
def on_join_tracking(data):
    join_room(f"tracking_{data['order_id']}")