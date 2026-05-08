from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.product import CartItem, Voucher
from app.models.chat import Notification
from datetime import datetime

order_bp = Blueprint('order', __name__)

@order_bp.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Keranjang kosong!', 'warning')
        return redirect(url_for('shop.cart'))
    total = sum(item.product.final_price * item.quantity for item in cart_items)
    return render_template('order/checkout.html', cart_items=cart_items, total=total)

@order_bp.route('/checkout/process', methods=['POST'])
@login_required
def process_checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return redirect(url_for('shop.cart'))

    address = request.form.get('address')
    payment_method = request.form.get('payment_method')
    is_cod = request.form.get('is_cod') == 'true'
    notes = request.form.get('notes', '')
    voucher_id = request.form.get('voucher_id')
    discount = float(request.form.get('discount', 0))

    subtotal = sum(float(item.product.final_price) * item.quantity for item in cart_items)
    total = max(0, subtotal - discount)

    order = Order(
        user_id=current_user.id,
        total_price=total,
        payment_method=payment_method,
        is_cod=is_cod,
        delivery_address=address,
        notes=notes,
        shipping_status='waiting',
        payment_status='paid' if is_cod else 'pending'
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.final_price
        )
        db.session.add(order_item)
        item.product.sold_count += item.quantity
        item.product.stock -= item.quantity
        db.session.delete(item)

    # Update voucher usage
    if voucher_id:
        voucher = Voucher.query.get(voucher_id)
        if voucher:
            voucher.used_count += 1

    # Buat notifikasi
    notif = Notification(
        user_id=current_user.id,
        type='order',
        title='✅ Pesanan Berhasil Dibuat!',
        message=f'Pesanan #ORDER-{order.id} sedang diproses',
        link=f'/orders/{order.id}'
    )
    db.session.add(notif)
    db.session.commit()

    flash('Pesanan berhasil dibuat! 🌹', 'success')
    return redirect(url_for('order.detail', order_id=order.id))

@order_bp.route('/orders')
@login_required
def history():
    status_filter = request.args.get('status', '')
    query = Order.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(shipping_status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('order/history.html', orders=orders, status_filter=status_filter)

@order_bp.route('/orders/<int:order_id>')
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('order.history'))
    return render_template('order/detail.html', order=order)

@order_bp.route('/orders/<int:order_id>/review', methods=['POST'])
@login_required
def add_review(order_id):
    from app.models.review import Review
    order = Order.query.get_or_404(order_id)
    product_id = request.form.get('product_id', type=int)
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )
    order.shipping_status = 'reviewed'
    db.session.add(review)
    db.session.commit()
    flash('Ulasan berhasil dikirim! 🌹', 'success')
    return redirect(url_for('order.detail', order_id=order_id))