from datetime import datetime, timezone
from app.extensions import db


class Listing(db.Model):
    __tablename__ = 'listings'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Listing information
    listing_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(50), index=True)
    condition = db.Column(db.String(50))
    sleeve_condition = db.Column(db.String(50))
    posted = db.Column(db.DateTime())
    uri = db.Column(db.String(255))
    resource_url = db.Column(db.String(255))
    
    # Price information
    price_value = db.Column(db.Float, db.CheckConstraint('price_value >= 0'), nullable=False)
    price_currency = db.Column(db.String(10))
    
    # Shipping information
    shipping_price = db.Column(db.Float)
    shipping_currency = db.Column(db.String(10))
    
    # Additional listing details
    weight = db.Column(db.Float)
    format_quantity = db.Column(db.Integer)
    external_id = db.Column(db.String(100))
    location = db.Column(db.String(255))
    comments = db.Column(db.Text)
    
    # Release information
    release_id = db.Column(db.String(50), nullable=False, index=True)
    release_title = db.Column(db.Text)
    release_year = db.Column(db.Integer(), index=True)
    release_resource_url = db.Column(db.String(255))
    release_uri = db.Column(db.String(255))
    
    # Artist information (denormalized for search/display)
    artist_names = db.Column(db.Text)
    primary_artist = db.Column(db.String(255), index=True)
    
    # Artist relationship (normalized)
    artist_id = db.Column(db.String(36), db.ForeignKey('artists.uuid'), nullable=True)
    artist = db.relationship('Artist', backref=db.backref('listings', lazy='dynamic'))
    
    # Label information
    label_names = db.Column(db.String(500))
    primary_label = db.Column(db.String(255))
    
    # Format information
    format_names = db.Column(db.String(255))
    primary_format = db.Column(db.String(100))
    
    # Genre and style
    genres = db.Column(db.String(500))
    styles = db.Column(db.String(500))
    
    # Country
    country = db.Column(db.String(100))
    
    # Additional release details
    catalog_number = db.Column(db.String(100))
    barcode = db.Column(db.String(100))
    master_id = db.Column(db.String(50))
    master_url = db.Column(db.String(255))
    
    # Images
    image_uri = db.Column(db.String(500))
    image_resource_url = db.Column(db.String(500))
    
    # Statistics
    release_community_have = db.Column(db.Integer)
    release_community_want = db.Column(db.Integer)
    
    # Timestamps
    export_timestamp = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert listing to dictionary for JSON serialization."""
        result = {
            'listing_id': self.listing_id,
            'status': self.status,
            'condition': self.condition,
            'sleeve_condition': self.sleeve_condition,
            'posted': self.posted.isoformat() if self.posted else None,
            'uri': self.uri,
            'resource_url': self.resource_url,
            'price_value': self.price_value,
            'price_currency': self.price_currency,
            'shipping_price': self.shipping_price,
            'shipping_currency': self.shipping_currency,
            'weight': self.weight,
            'format_quantity': self.format_quantity,
            'external_id': self.external_id,
            'location': self.location,
            'comments': self.comments,
            'release_id': self.release_id,
            'release_title': self.release_title,
            'release_year': self.release_year,
            'release_resource_url': self.release_resource_url,
            'release_uri': self.release_uri,
            'artist_names': self.artist_names,
            'primary_artist': self.primary_artist,
            'artist_id': self.artist_id,
            'label_names': self.label_names,
            'primary_label': self.primary_label,
            'format_names': self.format_names,
            'primary_format': self.primary_format,
            'genres': self.genres,
            'styles': self.styles,
            'country': self.country,
            'catalog_number': self.catalog_number,
            'barcode': self.barcode,
            'master_id': self.master_id,
            'master_url': self.master_url,
            'image_uri': self.image_uri,
            'image_resource_url': self.image_resource_url,
            'release_community_have': self.release_community_have,
            'release_community_want': self.release_community_want,
            'export_timestamp': self.export_timestamp.isoformat() if self.export_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include artist data if relationship is loaded
        if self.artist:
            result['artist'] = self.artist.to_dict()
            
        return result
    
    def __repr__(self):
        return f'<Listing {self.listing_id}: {self.release_title} by {self.primary_artist}>'

