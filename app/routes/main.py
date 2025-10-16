from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib
import secrets
import time
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService
from app.services.discogs_sync_service import DiscogsSyncService
from app.models.access_log import AccessLog
from app.extensions import db

bp = Blueprint('main', __name__)

def is_admin_authenticated():
    """Check if user is authenticated as admin."""
    return session.get('admin_authenticated', False)

def require_admin_auth(f):
    """Decorator to require admin authentication."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_admin_passphrase(passphrase):
    """Verify admin passphrase against stored hash."""
    stored_passphrase = current_app.config.get('ADMIN_PASSPHRASE')
    if not stored_passphrase:
        current_app.logger.warning("ADMIN_PASSPHRASE not configured")
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(passphrase, stored_passphrase)

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

@bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with passphrase authentication."""
    if request.method == 'POST':
        # Simple rate limiting - check for failed attempts
        failed_attempts = session.get('admin_login_attempts', 0)
        last_attempt = session.get('admin_login_last_attempt', 0)
        current_time = time.time()
        
        # Reset attempts after 15 minutes
        if current_time - last_attempt > 900:  # 15 minutes
            failed_attempts = 0
        
        # Block after 5 failed attempts for 15 minutes
        if failed_attempts >= 5:
            if current_time - last_attempt < 900:  # 15 minutes
                flash('Too many failed attempts. Please try again in 15 minutes.', 'error')
                return render_template('admin_login.html')
            else:
                failed_attempts = 0
        
        passphrase = request.form.get('passphrase', '').strip()
        
        if verify_admin_passphrase(passphrase):
            # Reset failed attempts on successful login
            session.pop('admin_login_attempts', None)
            session.pop('admin_login_last_attempt', None)
            session['admin_authenticated'] = True
            session.permanent = True  # Make session permanent
            flash('Successfully logged in as admin.', 'success')
            return redirect(url_for('main.admin'))
        else:
            # Increment failed attempts
            session['admin_login_attempts'] = failed_attempts + 1
            session['admin_login_last_attempt'] = current_time
            flash('Invalid passphrase. Please try again.', 'error')
    
    return render_template('admin_login.html')

@bp.route('/admin-logout', methods=['POST'])
def admin_logout():
    """Logout admin user."""
    session.pop('admin_authenticated', None)
    flash('Successfully logged out.', 'info')
    return redirect(url_for('main.admin_login'))

@bp.route('/admin')
@require_admin_auth
def admin():
    """Admin page for viewing access logs - requires authentication."""
    return render_template('admin.html')

@bp.route('/admin/access-logs')
@require_admin_auth
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
@require_admin_auth
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

@bp.route('/admin/clear-label-cache', methods=['POST'])
@require_admin_auth
def clear_label_cache():
    """Clear cached label overviews to force regeneration."""
    try:
        from app.models.label_info import LabelInfo
        
        # Clear all cached label overviews
        deleted_count = LabelInfo.query.delete()
        db.session.commit()
        
        current_app.logger.info(f"Cleared {deleted_count} cached label overviews")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} cached label overviews',
            'cleared_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error clearing label cache: {e}")
        return jsonify({'error': f'Failed to clear label cache: {str(e)}'}), 500

@bp.route('/admin/regenerate-label-overview', methods=['POST'])
@require_admin_auth
def regenerate_label_overview():
    """Regenerate overview for a specific label."""
    try:
        data = request.get_json()
        label_name = data.get('label_name')
        
        if not label_name:
            return jsonify({'error': 'Label name is required'}), 400
        
        from app.models.label_info import LabelInfo
        from app.services.gemini_service import GeminiService
        
        # Remove existing cache entry
        LabelInfo.query.filter_by(label_name=label_name).delete()
        
        # Generate new overview
        gemini = GeminiService()
        if gemini.is_available():
            overview = gemini.generate_label_overview(label_name)
            
            if overview:
                # Cache the new overview
                label_info = LabelInfo(
                    label_name=label_name,
                    overview=overview,
                    generated_by='gemini-1.5-flash'
                )
                db.session.add(label_info)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Regenerated overview for {label_name}',
                    'overview': overview
                })
            else:
                return jsonify({'error': 'Failed to generate overview'}), 500
        else:
            return jsonify({'error': 'Gemini service not available'}), 500
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error regenerating label overview: {e}")
        return jsonify({'error': f'Failed to regenerate overview: {str(e)}'}), 500
