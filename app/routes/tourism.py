from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.tourism import TourismSpot, TourismTicket
from app.models.chat import Notification
from datetime import datetime, date
import random
import string
import os

tourism_bp = Blueprint('tourism', __name__)

def generate_booking_code():
    return 'RV' + ''.join(random.choices(string.digits, k=8))

@tourism_bp.route('/wisata')
@login_required
def index():
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    search = request.args.get('search', '')

    query = TourismSpot.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    if city:
        query = query.filter(TourismSpot.city.ilike(f'%{city}%'))
    if search:
        query = query.filter(TourismSpot.name.ilike(f'%{search}%'))

    spots = query.order_by(TourismSpot.is_featured.desc(), TourismSpot.rating.desc()).all()
    featured = TourismSpot.query.filter_by(is_active=True, is_featured=True).limit(5).all()

    return render_template('tourism/index.html',
                           spots=spots, featured=featured,
                           category=category, city=city, search=search)

@tourism_bp.route('/wisata/<int:spot_id>')
@login_required
def detail(spot_id):
    spot = TourismSpot.query.get_or_404(spot_id)
    related = TourismSpot.query.filter_by(
        category=spot.category, is_active=True
    ).filter(TourismSpot.id != spot_id).limit(4).all()
    return render_template('tourism/detail.html', spot=spot, related=related, today=date.today())

@tourism_bp.route('/wisata/<int:spot_id>/book', methods=['POST'])
@login_required
def book(spot_id):
    spot = TourismSpot.query.get_or_404(spot_id)

    ticket_type = request.form.get('ticket_type', 'couple')
    quantity = int(request.form.get('quantity', 1))
    visit_date = datetime.strptime(request.form.get('visit_date'), '%Y-%m-%d').date()
    payment_method = request.form.get('payment_method', 'gopay')
    notes = request.form.get('notes', '')

    # Hitung harga
    prices = {'single': spot.price_min, 'couple': spot.price_min * 2, 'family': spot.price_min * 4}
    price_per = prices.get(ticket_type, spot.price_min)
    total = price_per * quantity

    ticket = TourismTicket(
        spot_id=spot_id,
        user_id=current_user.id,
        ticket_type=ticket_type,
        quantity=quantity,
        visit_date=visit_date,
        total_price=total,
        payment_method=payment_method,
        payment_status='paid',
        booking_code=generate_booking_code(),
        notes=notes
    )
    db.session.add(ticket)

    # Notifikasi
    notif = Notification(
        user_id=current_user.id,
        type='order',
        title='🎫 Tiket Wisata Berhasil!',
        message=f'Tiket {spot.name} untuk {visit_date.strftime("%d %b %Y")} sudah dipesan',
        link='/wisata/tiket'
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Tiket berhasil dipesan! Kode booking: {ticket.booking_code} 🎫', 'success')
    return redirect(url_for('tourism.my_tickets'))

@tourism_bp.route('/wisata/tiket')
@login_required
def my_tickets():
    tickets = TourismTicket.query.filter_by(user_id=current_user.id)\
        .order_by(TourismTicket.created_at.desc()).all()
    return render_template('tourism/tickets.html', tickets=tickets, today=date.today())

@tourism_bp.route('/wisata/tiket/<int:ticket_id>/cancel', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    ticket = TourismTicket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id:
        return jsonify({'success': False})
    ticket.status = 'cancelled'
    db.session.commit()
    return jsonify({'success': True})

# Admin routes
@tourism_bp.route('/admin/wisata')
@login_required
def admin_index():
    if not current_user.is_admin:
        return redirect(url_for('tourism.index'))
    spots = TourismSpot.query.order_by(TourismSpot.created_at.desc()).all()
    tickets = TourismTicket.query.order_by(TourismTicket.created_at.desc()).limit(10).all()
    total_revenue = sum(t.total_price for t in TourismTicket.query.filter_by(payment_status='paid').all())
    return render_template('tourism/admin.html', spots=spots, tickets=tickets, total_revenue=total_revenue)

@tourism_bp.route('/admin/wisata/add', methods=['POST'])
@login_required
def admin_add():
    if not current_user.is_admin:
        return jsonify({'success': False})

    import os
    from PIL import Image as PILImage

    spot = TourismSpot(
        name=request.form.get('name'),
        description=request.form.get('description'),
        location=request.form.get('location'),
        city=request.form.get('city'),
        province=request.form.get('province'),
        category=request.form.get('category'),
        price_min=int(request.form.get('price_min', 0)),
        price_max=int(request.form.get('price_max', 0)),
        opening_hours=request.form.get('opening_hours'),
        latitude=float(request.form.get('latitude', 0) or 0),
        longitude=float(request.form.get('longitude', 0) or 0),
        is_featured=request.form.get('is_featured') == 'true',
        facilities=request.form.get('facilities', '')
    )

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"tourism_{datetime.utcnow().timestamp()}.{ext}"
            folder = os.path.join('app', 'static', 'uploads', 'tourism')
            os.makedirs(folder, exist_ok=True)
            img = PILImage.open(file)
            img.thumbnail((800, 600))
            img.save(os.path.join(folder, filename))
            spot.image = filename

    db.session.add(spot)
    db.session.commit()
    flash('Destinasi wisata berhasil ditambahkan! 🗺️', 'success')
    return redirect(url_for('tourism.admin_index'))

@tourism_bp.route('/admin/wisata/<int:spot_id>/toggle', methods=['POST'])
@login_required
def admin_toggle(spot_id):
    if not current_user.is_admin:
        return jsonify({'success': False})
    spot = TourismSpot.query.get_or_404(spot_id)
    spot.is_active = not spot.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': spot.is_active})


    