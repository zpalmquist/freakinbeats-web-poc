from datetime import datetime
from app.extensions import db


class LabelInfo(db.Model):
    """SQLAlchemy model for cached label information from AI."""
    
    __tablename__ = 'label_info'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Label identification
    label_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # AI-generated content
    overview = db.Column(db.Text)
    
    # Metadata
    generated_by = db.Column(db.String(50), default='gemini-1.5-flash')  # LLM used to generate
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Cache control
    cache_valid = db.Column(db.Boolean, default=True)  # Invalidate to regenerate
    generation_error = db.Column(db.Text)  # Store any errors encountered
    
    def to_dict(self):
        """Convert label info to dictionary for JSON serialization."""
        return {
            'label_name': self.label_name,
            'overview': self.overview,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<LabelInfo {self.label_name}>'

