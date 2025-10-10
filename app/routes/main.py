from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/cart')
def cart():
    return render_template('cart.html')

@bp.route('/detail/<listing_id>')
def detail(listing_id):
    return render_template('detail.html')
