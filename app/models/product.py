from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    original_price = db.Column(db.Numeric(12, 2))
    discount_percent = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    image = db.Column(db.String(200), default='default_product.jpg')
    weight = db.Column(db.Float, default=0.5)
    location_lat = db.Column(db.Float)
    location_lng = db.Column(db.Float)
    is_cod = db.Column(db.Boolean, default=True)
    sold_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_flash_sale = db.Column(db.Boolean, default=False)
    flash_sale_price = db.Column(db.Numeric(12, 2))
    flash_sale_end = db.Column(db.DateTime)
    free_shipping = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)

    @property
    def final_price(self):
        if self.is_flash_sale and self.flash_sale_price:
            return self.flash_sale_price
        if self.discount_percent and self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price

    @property
    def discount_amount(self):
        return self.price - self.final_price

    def __repr__(self):
        return f'<Product {self.name}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20))  # discount, free_shipping, cashback
    value = db.Column(db.Numeric(12, 2))
    min_purchase = db.Column(db.Numeric(12, 2), default=0)
    max_discount = db.Column(db.Numeric(12, 2))
    quota = db.Column(db.Integer, default=100)
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    expired_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)