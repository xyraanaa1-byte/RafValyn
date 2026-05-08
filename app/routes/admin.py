from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.product import Product, CartItem, Voucher
from app.models.order import Order, OrderItem
from app.models.chat import Notification
from app.models.tourism import TourismSpot, TourismTicket
from datetime import datetime, timedelta, date
from functools import wraps
from sqlalchemy import func
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Akses ditolak!', 'danger')
            return redirect(url_for('shop.index'))
        return f(*args, **kwargs)
    return decorated

# ===== DASHBOARD =====
@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0
    total_tourism = TourismSpot.query.count()
    total_tickets = TourismTicket.query.count()
    tourism_revenue = db.session.query(func.sum(TourismTicket.total_price)).filter_by(payment_status='paid').scalar() or 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    pending_orders = Order.query.filter_by(shipping_status='waiting').count()
    low_stock = Product.query.filter(Product.stock < 5, Product.is_active == True).count()

    # Revenue 7 hari terakhir
    revenue_data = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        rev = db.session.query(func.sum(Order.total_price)).filter(
            func.date(Order.created_at) == day
        ).scalar() or 0
        revenue_data.append({'day': day.strftime('%a'), 'revenue': float(rev)})

    # Top produk
    top_products = Product.query.filter_by(is_active=True)\
        .order_by(Product.sold_count.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_tourism=total_tourism,
        total_tickets=total_tickets,
        tourism_revenue=tourism_revenue,
        recent_orders=recent_orders,
        recent_users=recent_users,
        pending_orders=pending_orders,
        low_stock=low_stock,
        revenue_data=revenue_data,
        top_products=top_products,
        now=datetime.utcnow()
    )

# ===== USERS =====
@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    query = User.query
    if search:
        query = query.filter(
            User.username.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%')
        )
    if role == 'admin':
        query = query.filter_by(is_admin=True)
    elif role == 'user':
        query = query.filter_by(is_admin=False)
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users, search=search, role=role,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Tidak bisa ubah diri sendiri!'})
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'success': True, 'is_admin': user.is_admin})

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Tidak bisa hapus diri sendiri!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/admin/users/<int:user_id>/detail')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    tickets = TourismTicket.query.filter_by(user_id=user_id).all()
    total_spent = sum(float(o.total_price) for o in orders)
    return render_template('admin/user_detail.html', user=user, orders=orders,
                           tickets=tickets, total_spent=total_spent,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/users/<int:user_id>/send-notif', methods=['POST'])
@login_required
@admin_required
def send_notif(user_id):
    title = request.json.get('title', 'Pesan dari Admin')
    message = request.json.get('message', '')
    notif = Notification(
        user_id=user_id,
        type='system',
        title=title,
        message=message,
        link='/home'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'success': True})

# ===== PRODUCTS =====
@admin_bp.route('/admin/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'low_stock':
        query = query.filter(Product.stock < 5)
    elif status == 'flash_sale':
        query = query.filter_by(is_flash_sale=True)
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/products.html', products=products,
                           category=category, search=search, status=status,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        from PIL import Image as PILImage
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        description = request.form.get('description', '')
        weight = float(request.form.get('weight', 0.5))
        is_cod = request.form.get('is_cod') == 'true'
        discount = int(request.form.get('discount_percent', 0))
        is_flash_sale = request.form.get('is_flash_sale') == 'true'
        flash_sale_price = request.form.get('flash_sale_price')

        product = Product(
            name=name, category=category, price=price,
            stock=stock, description=description, weight=weight,
            is_cod=is_cod, discount_percent=discount, is_active=True,
            is_flash_sale=is_flash_sale,
            flash_sale_price=float(flash_sale_price) if flash_sale_price else None
        )

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"product_{int(datetime.utcnow().timestamp())}.{ext}"
                    folder = os.path.join('app', 'static', 'uploads', 'products')
                    os.makedirs(folder, exist_ok=True)
                    img = PILImage.open(file)
                    img.thumbnail((800, 800))
                    img.save(os.path.join(folder, filename))
                    product.image = filename
                except Exception as e:
                    flash(f'Gagal upload foto: {str(e)}', 'warning')

        db.session.add(product)
        db.session.commit()
        flash('Produk berhasil ditambahkan! 🌹', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        from PIL import Image as PILImage
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.price = float(request.form.get('price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.description = request.form.get('description', '')
        product.weight = float(request.form.get('weight', 0.5))
        product.is_cod = request.form.get('is_cod') == 'true'
        product.discount_percent = int(request.form.get('discount_percent', 0))
        product.is_active = request.form.get('is_active') == 'true'
        product.is_flash_sale = request.form.get('is_flash_sale') == 'true'
        flash_price = request.form.get('flash_sale_price')
        product.flash_sale_price = float(flash_price) if flash_price else None

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"product_{int(datetime.utcnow().timestamp())}.{ext}"
                    folder = os.path.join('app', 'static', 'uploads', 'products')
                    os.makedirs(folder, exist_ok=True)
                    img = PILImage.open(file)
                    img.thumbnail((800, 800))
                    img.save(os.path.join(folder, filename))
                    product.image = filename
                except Exception as e:
                    flash(f'Gagal upload foto: {str(e)}', 'warning')

        db.session.commit()
        flash('Produk berhasil diupdate!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=product,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/admin/products/bulk', methods=['POST'])
@login_required
@admin_required
def bulk_action():
    action = request.json.get('action')
    ids = request.json.get('ids', [])
    products = Product.query.filter(Product.id.in_(ids)).all()
    for p in products:
        if action == 'activate': p.is_active = True
        elif action == 'deactivate': p.is_active = False
        elif action == 'delete': p.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'count': len(products)})

# ===== ORDERS =====
@admin_bp.route('/admin/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    payment = request.args.get('payment', '')
    search = request.args.get('search', '')
    query = Order.query
    if status:
        query = query.filter_by(shipping_status=status)
    if payment:
        query = query.filter_by(payment_method=payment)
    if search:
        query = query.join(User).filter(
            User.username.ilike(f'%{search}%') |
            Order.delivery_address.ilike(f'%{search}%')
        )
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/orders.html', orders=orders, status=status,
                           payment=payment, search=search,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.json.get('status')
    order.shipping_status = new_status
    status_messages = {
        'packed': 'Pesananmu sedang dikemas! 📦',
        'picked_up': 'Pesananmu sudah dijemput kurir 🚚',
        'on_the_way': 'Pesananmu sedang dalam perjalanan 🛵',
        'delivered': 'Pesananmu sudah tiba! ✅ Jangan lupa kasih ulasan ya'
    }
    if new_status in status_messages:
        notif = Notification(
            user_id=order.user_id,
            type='order',
            title='📦 Update Pesanan #ORDER-' + str(order.id),
            message=status_messages[new_status],
            link=f'/orders/{order.id}'
        )
        db.session.add(notif)
    db.session.commit()
    return jsonify({'success': True})

# ===== VOUCHERS =====
@admin_bp.route('/admin/vouchers')
@login_required
@admin_required
def vouchers():
    vouchers = Voucher.query.order_by(Voucher.created_at.desc()).all()
    return render_template('admin/vouchers.html', vouchers=vouchers,
                           pending_orders=Order.query.filter_by(shipping_status='waiting').count())

@admin_bp.route('/admin/vouchers/add', methods=['POST'])
@login_required
@admin_required
def add_voucher():
    code = request.form.get('code', '').upper().strip()
    if not code:
        flash('Kode voucher tidak boleh kosong!', 'danger')
        return redirect(url_for('admin.vouchers'))
    existing = Voucher.query.filter_by(code=code).first()
    if existing:
        flash('Kode voucher sudah ada!', 'danger')
        return redirect(url_for('admin.vouchers'))
    voucher = Voucher(
        code=code,
        type=request.form.get('type'),
        value=float(request.form.get('value', 0)),
        min_purchase=float(request.form.get('min_purchase', 0)),
        max_discount=float(request.form.get('max_discount', 0)) or None,
        quota=int(request.form.get('quota', 100)),
        expired_at=datetime.utcnow() + timedelta(days=int(request.form.get('days', 30)))
    )
    db.session.add(voucher)
    db.session.commit()
    flash(f'Voucher {code} berhasil dibuat!', 'success')
    return redirect(url_for('admin.vouchers'))

@admin_bp.route('/admin/vouchers/<int:voucher_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_voucher(voucher_id):
    voucher = Voucher.query.get_or_404(voucher_id)
    voucher.is_active = not voucher.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': voucher.is_active})

@admin_bp.route('/admin/vouchers/<int:voucher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_voucher(voucher_id):
    voucher = Voucher.query.get_or_404(voucher_id)
    db.session.delete(voucher)
    db.session.commit()
    return jsonify({'success': True})

# ===== STATS API =====
@admin_bp.route('/admin/api/stats')
@login_required
@admin_required
def api_stats():
    revenue_today = db.session.query(func.sum(Order.total_price)).filter(
        func.date(Order.created_at) == date.today()
    ).scalar() or 0
    orders_today = Order.query.filter(
        func.date(Order.created_at) == date.today()
    ).count()
    new_users_today = User.query.filter(
        func.date(User.created_at) == date.today()
    ).count()
    return jsonify({
        'revenue_today': float(revenue_today),
        'orders_today': orders_today,
        'new_users_today': new_users_today,
        'pending_orders': Order.query.filter_by(shipping_status='waiting').count()
    })