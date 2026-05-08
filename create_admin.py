from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='admin@rafvalyn.com').first()
    if not user:
        user = User(
            username='admin',
            email='admin@rafvalyn.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print('Admin dibuat! Email: admin@rafvalyn.com | Password: admin123')
    else:
        user.is_admin = True
        db.session.commit()
        print('User sudah jadi admin!')