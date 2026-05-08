from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Numeric(12, 2))
    payment_method = db.Column(db.String(50))  # gopay, ovo, dana, dll
    payment_status = db.Column(db.String(20), default='pending')
    is_cod = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Alamat pengiriman
    delivery_address = db.Column(db.Text)
    delivery_lat = db.Column(db.Float)
    delivery_lng = db.Column(db.Float)
    
    # Status pengiriman
    shipping_status = db.Column(db.String(30), default='waiting')
    # waiting → packed → picked_up → on_the_way → delivered
    
    courier_lat = db.Column(db.Float)   # posisi kurir realtime
    courier_lng = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(12, 2))
    product = db.relationship('Product')
    