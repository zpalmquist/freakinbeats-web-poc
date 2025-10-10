from datetime import datetime
from app.extensions import db


class AccessLog(db.Model):
    """SQLAlchemy model for tracking website access logs."""
    
    __tablename__ = 'access_logs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Request information
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, etc.
    path = db.Column(db.String(500), nullable=False, index=True)
    query_string = db.Column(db.String(500))
    full_url = db.Column(db.String(1000))
    
    # Client information
    ip_address = db.Column(db.String(50), index=True)
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(500))
    
    # Response information
    status_code = db.Column(db.Integer, index=True)
    response_time_ms = db.Column(db.Float)  # Response time in milliseconds
    
    # Additional metadata
    endpoint = db.Column(db.String(100))  # Flask endpoint name
    
    def to_dict(self):
        """Convert access log to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'method': self.method,
            'path': self.path,
            'query_string': self.query_string,
            'full_url': self.full_url,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'endpoint': self.endpoint
        }
    
    def __repr__(self):
        return f'<AccessLog {self.id}: {self.method} {self.path} [{self.status_code}]>'

