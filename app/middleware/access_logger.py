"""
Access logging middleware for Flask application.

Automatically logs all HTTP requests to the database.
"""

import time
from flask import request, g
from app.extensions import db
from app.models.access_log import AccessLog


def init_access_logging(app):
    """Initialize access logging middleware for the Flask app."""
    
    @app.before_request
    def before_request():
        """Record the start time of the request."""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Log the request details after processing."""
        try:
            # Calculate response time
            response_time = None
            if hasattr(g, 'start_time'):
                response_time = (time.time() - g.start_time) * 1000  # Convert to ms
            
            # Get request information
            query_string = request.query_string.decode('utf-8') if request.query_string else None
            full_url = request.url if request.url else None
            
            # Get client information
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length
            referrer = request.headers.get('Referer', '')[:500]
            
            # Create access log entry
            access_log = AccessLog(
                method=request.method,
                path=request.path,
                query_string=query_string,
                full_url=full_url,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                status_code=response.status_code,
                response_time_ms=response_time,
                endpoint=request.endpoint
            )
            
            # Add to database
            db.session.add(access_log)
            db.session.commit()
            
        except Exception as e:
            # Don't let logging errors break the application
            app.logger.error(f"Error logging access: {e}")
            db.session.rollback()
        
        return response
    
    app.logger.info("Access logging middleware initialized")

