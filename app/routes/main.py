from flask import Blueprint, render_template, request, jsonify
from app.services.inventory_service import InventoryService

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
        
        inventory_service = InventoryService()
        validated_items = []
        total = 0
        
        for item in cart_data['items']:
            listing_id = item.get('listing_id')
            quantity = item.get('quantity', 1)
            
            # Validate item still exists and get current price
            listing = inventory_service.get_item_by_listing_id(listing_id)
            if not listing:
                return jsonify({'error': f'Item {listing_id} no longer available'}), 400
            
            # Calculate item total
            price = float(listing.get('price', 0))
            item_total = price * quantity
            total += item_total
            
            validated_items.append({
                'listing_id': listing_id,
                'title': listing.get('title'),
                'artist': listing.get('artist'),
                'price': price,
                'quantity': quantity,
                'item_total': item_total,
                'currency': listing.get('currency', '$')
            })
        
        return jsonify({
            'items': validated_items,
            'total': total,
            'currency': validated_items[0]['currency'] if validated_items else '$'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to validate cart'}), 500
