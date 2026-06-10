import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-ganti-nanti")

    # =============================================
    # DATABASE - MySQL Aiven (dengan SSL)
    # =============================================
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # SSL Certificate untuk Aiven
    ca_cert_path = os.path.join(os.path.dirname(__file__), "ca.pem")
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"ssl": {"ca": ca_cert_path}}}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =============================================
    # UPLOAD FOTO
    # =============================================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

    # Cloudinary (untuk foto permanen di Render)
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # =============================================
    # MAIL
    # =============================================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
