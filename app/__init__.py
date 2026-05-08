from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth
from app.config import Config
from datetime import timedelta

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO(async_mode='threading')
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inisialisasi semua ekstensi
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    oauth.init_app(app)

    app.jinja_env.globals['timedelta'] = timedelta

    # Konfigurasi login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu!'
    login_manager.login_message_category = 'warning'

    # Daftarkan semua blueprint
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.shop import shop_bp
    from app.routes.order import order_bp
    from app.routes.payment import payment_bp
    from app.routes.tracking import tracking_bp
    from app.routes.message import message_bp
    from app.routes.admin import admin_bp
    from app.routes.chat import chat_bp
    from app.routes.notification import notif_bp
    from app.routes.journal import journal_bp
    from app.routes.tourism import tourism_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(tourism_bp)

    # User loader — WAJIB ada supaya Flask-Login bisa cari user
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app