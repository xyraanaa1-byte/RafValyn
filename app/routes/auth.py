from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from flask import send_from_directory
import os
from flask import send_from_directory, make_response

auth_bp = Blueprint('auth', __name__)

# HALAMAN WELCOME
@auth_bp.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))
    return render_template('welcome.html')

# HALAMAN LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Email: {email}")  # ← tambah ini
        print(f"Password: {password}")  # ← tambah ini
        
        user = User.query.filter_by(email=email).first()
        
        print(f"User ditemukan: {user}")  # ← tambah ini
        
        if user and user.check_password(password):
            login_user(user)
            flash('Selamat datang kembali! 🌹', 'success')
            return redirect(url_for('shop.index'))
        else:
            flash('Email atau password salah!', 'danger')

    return render_template('auth/login.html')

# HALAMAN REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validasi
        if password != confirm_password:
            flash('Password tidak cocok!', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password minimal 8 karakter!', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username sudah dipakai!', 'danger')
            return render_template('auth/register.html')

        # Buat user baru
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Akun berhasil dibuat! Silakan login 🌹', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sampai jumpa! 🌹', 'success')
    return redirect(url_for('auth.welcome'))

@auth_bp.route('/static/sw.js')
def sw():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@auth_bp.route('/offline')
def offline():
    return render_template('offline.html')