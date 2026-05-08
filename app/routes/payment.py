from flask import Blueprint, render_template
from flask_login import login_required

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment')
@login_required
def method():
    return render_template('shop/index.html')