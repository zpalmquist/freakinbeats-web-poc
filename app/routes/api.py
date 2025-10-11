from flask import Blueprint, jsonify, request
from app.services.inventory_service import InventoryService
from app.models.access_log import AccessLog

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/data')
def get_data():
    """Get all listings."""
    service = InventoryService()
    data = service.get_all_items()
    return jsonify(data)

@bp.route('/data/<int:id>')
def get_listing_by_id(id):
    """Get a specific listing by database ID."""
    service = InventoryService()
    listing = service.get_item_by_id(id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@bp.route('/data/<listing_id>')
def get_listing(listing_id):
    """Get a specific listing by Discogs listing ID."""
    service = InventoryService()
    listing = service.get_item_by_listing_id(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@bp.route('/detail/<int:id>')
def get_listing_detail_by_id(id):
    """Get detailed listing information including videos by database ID."""
    service = InventoryService()
    listing = service.get_item_with_videos_by_id(id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@bp.route('/detail/<listing_id>')
def get_listing_detail(listing_id):
    """Get detailed listing information including videos by Discogs listing ID."""
    service = InventoryService()
    listing = service.get_item_with_videos(listing_id)
    if listing:
        return jsonify(listing)
    return jsonify({'error': 'Listing not found'}), 404

@bp.route('/search')
def search_listings():
    """Search listings with optional filters."""
    service = InventoryService()
    
    query = request.args.get('q')
    artist = request.args.get('artist')
    genre = request.args.get('genre')
    format_type = request.args.get('format')
    
    data = service.search_items(
        query=query,
        artist=artist,
        genre=genre,
        format_type=format_type
    )
    return jsonify(data)

@bp.route('/filter')
def filter_listings():
    """Filter listings with multiple criteria."""
    service = InventoryService()
    
    query = request.args.get('q')
    artist = request.args.get('artist')
    label = request.args.get('label')
    year = request.args.get('year')
    condition = request.args.get('condition')
    sleeve_condition = request.args.get('sleeve_condition')
    
    data = service.filter_items(
        query=query,
        artist=artist,
        label=label,
        year=year,
        condition=condition,
        sleeve_condition=sleeve_condition
    )
    return jsonify(data)

@bp.route('/facets')
def get_facets():
    """Get filter facets with counts."""
    service = InventoryService()
    facets = service.get_filter_facets()
    return jsonify(facets)

@bp.route('/stats')
def get_stats():
    """Get inventory statistics."""
    service = InventoryService()
    stats = service.get_stats()
    return jsonify(stats)

@bp.route('/logs')
def get_access_logs():
    """Get access logs with optional filters."""
    limit = request.args.get('limit', 100, type=int)
    path = request.args.get('path')
    method = request.args.get('method')
    ip = request.args.get('ip')
    
    # Build query
    query = AccessLog.query
    
    if path:
        query = query.filter(AccessLog.path.like(f'%{path}%'))
    if method:
        query = query.filter(AccessLog.method == method.upper())
    if ip:
        query = query.filter(AccessLog.ip_address == ip)
    
    # Get logs ordered by most recent first
    logs = query.order_by(AccessLog.timestamp.desc()).limit(limit).all()
    
    return jsonify([log.to_dict() for log in logs])

@bp.route('/logs/stats')
def get_log_stats():
    """Get access log statistics."""
    from sqlalchemy import func
    
    total_requests = AccessLog.query.count()
    
    # Requests by method
    by_method = AccessLog.query.with_entities(
        AccessLog.method,
        func.count(AccessLog.id).label('count')
    ).group_by(AccessLog.method).all()
    
    # Requests by status code
    by_status = AccessLog.query.with_entities(
        AccessLog.status_code,
        func.count(AccessLog.id).label('count')
    ).group_by(AccessLog.status_code).all()
    
    # Top paths
    top_paths = AccessLog.query.with_entities(
        AccessLog.path,
        func.count(AccessLog.id).label('count')
    ).group_by(AccessLog.path).order_by(func.count(AccessLog.id).desc()).limit(10).all()
    
    # Average response time
    avg_response_time = AccessLog.query.with_entities(
        func.avg(AccessLog.response_time_ms)
    ).scalar()
    
    return jsonify({
        'total_requests': total_requests,
        'by_method': {method: count for method, count in by_method},
        'by_status': {status: count for status, count in by_status},
        'top_paths': [{'path': path, 'count': count} for path, count in top_paths],
        'avg_response_time_ms': round(avg_response_time, 2) if avg_response_time else None
    })
