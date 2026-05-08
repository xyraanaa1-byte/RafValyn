from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
import os
from werkzeug.utils import secure_filename
from PIL import Image

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file, folder='profiles'):
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    new_filename = f"{current_user.id}_{name}{ext}"
    upload_path = os.path.join('app', 'static', 'uploads', folder)
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, new_filename)
    img = Image.open(file)
    img.thumbnail((400, 400))
    img.save(filepath)
    return new_filename

@profile_bp.route('/profile')
@login_required
def view():
    return render_template('profile/view.html', user=current_user)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if username != current_user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('Username sudah dipakai!', 'danger')
                return render_template('profile/edit.html', user=current_user)

        current_user.username = username
        current_user.bio = bio
        current_user.phone = phone
        current_user.address = address

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = save_photo(file)
                current_user.profile_photo = filename

        db.session.commit()
        flash('Profil berhasil diperbarui! 🌹', 'success')
        return redirect(url_for('profile.view'))

    return render_template('profile/edit.html', user=current_user)