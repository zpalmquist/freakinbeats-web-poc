from uuid import uuid4
from datetime import datetime
from app.extensions import db


class RecordLabel(db.Model):
    """Normalized record label model."""
    
    __tablename__ = 'record_labels'
    
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    listings = db.relationship('Listing', backref='label', lazy='dynamic')
    
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
        }
    
    def __repr__(self):
        return f'<RecordLabel {self.name}>'
