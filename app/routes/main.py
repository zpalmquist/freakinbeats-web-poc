from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService
from app.services.discogs_sync_service import DiscogsSyncService
from app.models.access_log import AccessLog
from app.extensions import db

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
            'total': total_price,
            'currency': currency,
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

@bp.route('/admin')
def admin():
    """Admin page for viewing access logs - standalone page accessible only via direct URL."""
    return render_template('admin.html')

@bp.route('/admin/access-logs')
def get_access_logs():
    """API endpoint to fetch access logs with pagination and filtering."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        method_filter = request.args.get('method', '')
        
        # Build query
        query = AccessLog.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    AccessLog.path.contains(search),
                    AccessLog.ip_address.contains(search),
                    AccessLog.user_agent.contains(search)
                )
            )
        
        if status_filter:
            query = query.filter(AccessLog.status_code == int(status_filter))
        
        if method_filter:
            query = query.filter(AccessLog.method == method_filter)
        
        # Order by most recent first
        query = query.order_by(AccessLog.timestamp.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Convert to dict format
        logs = [log.to_dict() for log in pagination.items]
        
        return jsonify({
            'logs': logs,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch access logs: {str(e)}'}), 500

@bp.route('/admin/sync-discogs', methods=['POST'])
def sync_discogs():
    """Trigger Discogs synchronization from admin panel."""
    try:
        # Check if Discogs credentials are configured
        token = current_app.config.get('DISCOGS_TOKEN')
        seller_username = current_app.config.get('DISCOGS_SELLER_USERNAME')
        user_agent = current_app.config.get('DISCOGS_USER_AGENT')
        
        if not token:
            return jsonify({'error': 'Discogs token not configured'}), 400
        
        if not seller_username:
            return jsonify({'error': 'Discogs seller username not configured'}), 400
        
        # Initialize sync service
        sync_service = DiscogsSyncService(
            token=token,
            seller_username=seller_username,
            user_agent=user_agent
        )
        
        # Perform sync
        current_app.logger.info("Admin triggered Discogs sync")
        stats = sync_service.sync_all_listings()
        
        return jsonify({
            'success': True,
            'message': 'Discogs sync completed successfully',
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error during Discogs sync: {e}")
        return jsonify({'error': f'Discogs sync failed: {str(e)}'}), 500
