from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, CartItem, Voucher
from app.models.order import Order, OrderItem
from datetime import datetime
from sqlalchemy import or_

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')
@shop_bp.route('/home')
@login_required
def index():
    products = Product.query.filter_by(is_active=True).order_by(Product.sold_count.desc()).limit(8).all()
    flash_sales = Product.query.filter_by(is_active=True, is_flash_sale=True).limit(6).all()
    return render_template('shop/index.html', products=products, flash_sales=flash_sales)

@shop_bp.route('/shop/products')
@login_required
def products():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'terlaris')
    page = request.args.get('page', 1, type=int)

    query = Product.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if sort == 'terlaris':
        query = query.order_by(Product.sold_count.desc())
    elif sort == 'termurah':
        query = query.order_by(Product.price.asc())
    elif sort == 'termahal':
        query = query.order_by(Product.price.desc())
    elif sort == 'terbaru':
        query = query.order_by(Product.created_at.desc())
    elif sort == 'diskon':
        query = query.filter(Product.discount_percent > 0).order_by(Product.discount_percent.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    return render_template('shop/products.html', products=products, category=category, search=search, sort=sort)

@shop_bp.route('/shop/product/<int:product_id>')
@login_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter_by(category=product.category, is_active=True).filter(Product.id != product_id).limit(4).all()
    return render_template('shop/detail.html', product=product, related=related)

@shop_bp.route('/shop/flash-sale')
@login_required
def flash_sale():
    products = Product.query.filter_by(is_active=True, is_flash_sale=True).all()
    return render_template('shop/flash_sale.html', products=products)

@shop_bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.final_price * item.quantity for item in cart_items)
    return render_template('shop/cart.html', cart_items=cart_items, total=total)

@shop_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        return jsonify({'success': False, 'message': 'Stok habis!'})

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        if cart_item.quantity >= product.stock:
            return jsonify({'success': False, 'message': 'Stok tidak mencukupi!'})
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count})

@shop_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'success': False})
    action = request.json.get('action')
    if action == 'increase':
        if item.quantity >= item.product.stock:
            return jsonify({'success': False, 'message': 'Stok tidak mencukupi!'})
        item.quantity += 1
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
        else:
            db.session.delete(item)
            db.session.commit()
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
            return jsonify({'success': True, 'cart_count': cart_count, 'deleted': True})
    db.session.commit()
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count, 'quantity': item.quantity,
                    'subtotal': float(item.product.final_price * item.quantity)})

@shop_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return jsonify({'success': False})
    db.session.delete(item)
    db.session.commit()
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count})

@shop_bp.route('/cart/count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})

@shop_bp.route('/voucher/check', methods=['POST'])
@login_required
def check_voucher():
    code = request.json.get('code', '').upper()
    total = request.json.get('total', 0)
    voucher = Voucher.query.filter_by(code=code, is_active=True).first()

    if not voucher:
        return jsonify({'success': False, 'message': 'Kode voucher tidak valid!'})
    if voucher.quota <= voucher.used_count:
        return jsonify({'success': False, 'message': 'Voucher sudah habis!'})
    if voucher.expired_at and voucher.expired_at < datetime.utcnow():
        return jsonify({'success': False, 'message': 'Voucher sudah kadaluarsa!'})
    if total < float(voucher.min_purchase):
        return jsonify({'success': False, 'message': f'Minimum pembelian Rp {int(voucher.min_purchase):,}'})

    discount = 0
    if voucher.type == 'discount':
        discount = float(voucher.value) / 100 * total
        if voucher.max_discount:
            discount = min(discount, float(voucher.max_discount))
    elif voucher.type == 'free_shipping':
        discount = 0
    elif voucher.type == 'cashback':
        discount = float(voucher.value)

    return jsonify({
        'success': True,
        'voucher_id': voucher.id,
        'type': voucher.type,
        'discount': discount,
        'message': f'Voucher berhasil! Hemat Rp {int(discount):,}'
    })