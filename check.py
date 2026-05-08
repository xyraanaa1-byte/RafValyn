from app import create_app

app = create_app()
with app.app_context():
    env = app.jinja_env
    try:
        env.get_template('shop/detail.html')
        print('Template OK!')
    except Exception as e:
        print('ERROR:', e)