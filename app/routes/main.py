from flask import Blueprint, render_template, request, jsonify
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService

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

@bp.route('/checkout')
def checkout():
    """Checkout page for processing payment."""
    return render_template('checkout.html')

@bp.route('/checkout/validate', methods=['POST'])
def validate_checkout():
    """Validate cart items and calculate totals for checkout."""
    try:
        cart_data = request.get_json()
        if not cart_data or not cart_data.get('items'):
            return jsonify({'error': 'Cart is empty'}), 400
        
        cart_service = CartService()
        
        # Use CartService for validation
        is_valid, validated_items, total_price, currency = cart_service.validate_cart(cart_data['items'])
        
        if not is_valid:
            return jsonify({'error': 'Cart validation failed'}), 400
        
        # Get cart summary with tax, shipping, etc.
        cart_summary = cart_service.calculate_cart_summary(validated_items)
        
        return jsonify({
            'items': validated_items,
            'summary': cart_summary,
            'is_valid': True
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to validate cart: {str(e)}'}), 500

@bp.route('/checkout/prepare-payment', methods=['POST'])
def prepare_payment():
    """Prepare cart data for Stripe payment processing."""
    try:
        cart_data = request.get_json()
        if not cart_data or not cart_data.get('items'):
            return jsonify({'error': 'Cart is empty'}), 400
        
        cart_service = CartService()
        
        # Get Stripe-formatted cart data
        stripe_data = cart_service.get_cart_for_stripe(cart_data['items'])
        
        return jsonify({
            'stripe_data': stripe_data,
            'success': True
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to prepare payment: {str(e)}'}), 500