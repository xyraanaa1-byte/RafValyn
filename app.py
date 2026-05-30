from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ============================================
# PATH DATABASE YANG BENAR (ke folder app/)
# ============================================

# Ambil direktori tempat file app.py berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke database yang ada di folder app/
# Karena app.py di root, dan database di folder app/
db_path = os.path.join(BASE_DIR, 'app', 'valentine.db')

print(f"📁 Database path: {db_path}")  # Buat debugging
print(f"📁 File exists: {os.path.exists(db_path)}")  # Cek apakah file ada

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================
# IMPORT MODEL (Sesuaikan dengan punyamu)
# ============================================

# Contoh import model (ganti dengan yang sesuai)
# from app.models import User, Product, Order
# Atau jika model ada di file terpisah:
# import app.models

# ============================================
# DEBUG: Lihat daftar tabel
# ============================================

with app.app_context():
    # Cek apakah koneksi berhasil
    try:
        # Coba query ke database
        result = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in result]
        print(f"✅ Connected to database. Tables found: {tables}")
    except Exception as e:
        print(f"❌ Database error: {e}")

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return "Welcome to Valentine App!"

# Import routes kamu di sini (setelah db dibuat)
# from app.routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)