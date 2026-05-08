from app import db
from datetime import datetime

class TourismSpot(db.Model):
    __tablename__ = 'tourism_spots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category = db.Column(db.String(50))  # pantai, taman, restoran, hotel, dll
    image = db.Column(db.String(200))
    price_min = db.Column(db.Integer, default=0)
    price_max = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=4.5)
    total_reviews = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    opening_hours = db.Column(db.String(100))
    facilities = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship('TourismTicket', backref='spot', lazy=True)

class TourismTicket(db.Model):
    __tablename__ = 'tourism_tickets'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('tourism_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_type = db.Column(db.String(50))  # couple, single, family
    quantity = db.Column(db.Integer, default=1)
    visit_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')
    status = db.Column(db.String(20), default='active')  # active, used, cancelled
    booking_code = db.Column(db.String(20), unique=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])