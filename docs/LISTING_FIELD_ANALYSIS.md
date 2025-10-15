# Listing Model Field Analysis

## Overview

Analysis of Discogs API response to determine minimal required fields for normalized schema with Artist, Genre, Style, and Label tables.

---

## Current Discogs API Response Structure

Based on `tests/fixtures/real_discogs_data.json`, each listing contains:

### Top-Level Listing Fields
```json
{
  "id": 3863883322,                           // Discogs listing ID
  "uri": "...",                               // Web URL for this listing
  "status": "For Sale",                       // Sale status
  "condition": "Mint (M)",                    // Media condition
  "sleeve_condition": "Mint (M)",             // Sleeve condition
  "comments": "sealed mint...",               // Seller notes
  "posted": "2025-10-10T11:41:52-07:00",     // When listed
  "price": {
    "value": 50.0,
    "currency": "USD"
  },
  "shipping_price": {
    "value": 6.5,
    "currency": "USD"
  },
  "weight": 230.0,
  "format_quantity": 1,
  "external_id": "Colin purchased...",        // Your custom comment
  "location": "CB1",                          // Your storage location
  "quantity": 1
}
```

### Nested Release Fields
```json
{
  "release": {
    "id": 34748517,                          // Discogs release ID
    "title": "Speaking In Code",             // Album/Release title
    "artist": "DJ COUNSELLING",              // Primary artist (string)
    "year": 2025,                            // Release year
    "label": "Ten Flowers",                  // Primary label (string)
    "catalog_number": "20 B2",               // Label catalog number
    "format": "LP, Album, Num",              // Format description
    "thumbnail": "...",                      // Small image URL
    "images": [                              // Array of images
      {
        "type": "primary",
        "uri": "https://...",                // Full-size image
        "uri150": "https://...",             // Thumbnail
        "width": 600,
        "height": 600
      }
    ],
    "stats": {
      "community": {
        "in_wantlist": 4,                   // Popularity metric
        "in_collection": 6                  // Popularity metric
      }
    }
  }
}
```

### Fields NOT in Basic Response (Require Additional API Call)
These require calling `/releases/{id}` endpoint:
- `genres`: ["Electronic", "Jazz"]
- `styles`: ["House", "Deep House", "Ambient"]
- `tracklist`: Full track listing
- `artists`: Detailed artist array with IDs
- `labels`: Detailed label array with IDs
- `master_id`: Master release ID
- `master_url`: Master release URL

---

## Current Model vs Required Fields

### ❌ Fields You're Storing But DON'T Need

| Field | Why Not Needed | Alternative |
|-------|---------------|-------------|
| `artist_names` | Redundant with `Artist` table | Use relationship |
| `label_names` | Redundant with `Label` table | Use relationship |
| `format_names` | Overly specific | Store in `Format` table if needed |
| `release_uri` | Just a URL construction | Build from `release_id` |
| `release_resource_url` | Same as above | Build from `release_id` |
| `uri` | Can construct from `listing_id` | Build dynamically |
| `resource_url` | Same as above | Build dynamically |
| `image_resource_url` | Discogs API URL, not display | Use `image_uri` only |
| `shipping_price` | Your shipping is flat rate | Calculate in cart |
| `shipping_currency` | Always USD for you | Use constant |
| `weight` | Not displayed anywhere | Only if shipping varies |
| `barcode` | Not used in UI | Only for detailed view |
| `master_id` | Not used currently | Add if building "versions" feature |
| `master_url` | Can construct from `master_id` | Build dynamically |
| `export_timestamp` | Redundant with `updated_at` | Use `updated_at` |
| `release_community_have` | Changes frequently, stale | Fetch live if needed |
| `release_community_want` | Same as above | Fetch live if needed |

### ✅ Fields You NEED to Keep

#### Core Listing Fields (Your inventory)
```python
# Identity
listing_id          # Discogs listing ID (unique)
status             # For Sale, Sold, Removed, Hold

# Condition  
condition          # Media condition
sleeve_condition   # Sleeve condition

# Pricing
price_value        # Your asking price
price_currency     # USD

# Inventory Management
posted             # When you listed it
location           # Your storage location (CB1, etc.)
quantity           # Stock quantity
external_id        # Your custom reference
comments           # Your notes about this copy

# Soft delete (Phase 1)
is_active          # For soft deletes
removed_at         # When marked inactive

# Change detection (Phase 1)
content_hash       # For change detection
```

#### Release Reference Fields (Link to Release table)
```python
# Minimal release info for display
release_id         # Discogs release ID
release_title      # "Speaking In Code"
release_year       # 2025
image_uri          # Primary image URL

# Relationships (Phase 4)
artist_id          # FK to artists.uuid
label_id           # FK to record_labels.uuid

# Optional denormalized (for speed)
primary_artist     # "DJ COUNSELLING" (cached)
primary_label      # "Ten Flowers" (cached)
catalog_number     # "20 B2"
primary_format     # "LP"
```

---

## Proposed New Normalized Schema

### Listings Table (Simplified)
```python
class Listing(db.Model):
    __tablename__ = 'listings'
    
    # Primary key
    uuid = db.Column(db.String(36), primary_key=True)
    
    # Discogs reference
    listing_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    release_id = db.Column(db.String(50), nullable=False, index=True)
    
    # Status & availability
    status = db.Column(db.Enum('For Sale', 'Sold', 'Removed', 'Hold'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Condition
    media_condition = db.Column(db.String(50), nullable=False)
    sleeve_condition = db.Column(db.String(50), nullable=False)
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Your inventory data
    location = db.Column(db.String(50))          # Your storage location
    external_id = db.Column(db.String(100))      # Your reference
    comments = db.Column(db.Text)                # Your notes
    posted_at = db.Column(db.DateTime)
    
    # Display fields (denormalized for speed)
    release_title = db.Column(db.String(500), nullable=False, index=True)
    release_year = db.Column(db.Integer, index=True)
    image_uri = db.Column(db.String(500))
    primary_artist = db.Column(db.String(255), index=True)  # Cached
    primary_label = db.Column(db.String(255))               # Cached
    primary_format = db.Column(db.String(100))
    catalog_number = db.Column(db.String(100))
    
    # Foreign keys (Phase 4)
    artist_id = db.Column(db.String(36), db.ForeignKey('artists.uuid'), nullable=True)
    label_id = db.Column(db.String(36), db.ForeignKey('record_labels.uuid'), nullable=True)
    
    # Optimization fields
    content_hash = db.Column(db.String(64), index=True)
    
    # Timestamps
    removed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    artist = db.relationship('Artist', backref=db.backref('listings', lazy='dynamic'))
    label = db.relationship('RecordLabel', backref=db.backref('listings', lazy='dynamic'))
    genres = db.relationship('Genre', secondary='listing_genres', backref='listings')
    styles = db.relationship('Style', secondary='listing_styles', backref='listings')
```

**Field Count**: ~23 fields (down from ~50)

---

### Artists Table
```python
class Artist(db.Model):
    __tablename__ = 'artists'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Optional enrichment data
    discogs_id = db.Column(db.String(50), nullable=True, unique=True)
    description = db.Column(db.Text, nullable=True)
    image_uri = db.Column(db.String(500), nullable=True)
    
    # Stats
    listing_count = db.Column(db.Integer, default=0)  # Denormalized count
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Source**: Extracted from `release.artist` (string) in listings API response

---

### Record Labels Table
```python
class RecordLabel(db.Model):
    __tablename__ = 'record_labels'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Optional enrichment data
    discogs_id = db.Column(db.String(50), nullable=True, unique=True)
    description = db.Column(db.Text, nullable=True)
    image_uri = db.Column(db.String(500), nullable=True)
    
    # Stats
    listing_count = db.Column(db.Integer, default=0)  # Denormalized count
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Source**: Extracted from `release.label` (string) in listings API response

---

### Genres Table (Requires Additional API Call)
```python
class Genre(db.Model):
    __tablename__ = 'genres'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # Stats
    listing_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Source**: Must call `/releases/{id}` to get genres array  
**Note**: Not in basic listing response, requires separate API call

---

### Styles Table (Requires Additional API Call)
```python
class Style(db.Model):
    __tablename__ = 'styles'
    
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # Optional: Link to parent genre
    genre_id = db.Column(db.String(36), db.ForeignKey('genres.uuid'), nullable=True)
    
    # Stats
    listing_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Source**: Must call `/releases/{id}` to get styles array  
**Note**: Not in basic listing response, requires separate API call

---

### Many-to-Many Junction Tables

#### listing_genres
```python
listing_genres = db.Table('listing_genres',
    db.Column('listing_uuid', db.String(36), db.ForeignKey('listings.uuid'), primary_key=True),
    db.Column('genre_uuid', db.String(36), db.ForeignKey('genres.uuid'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
```

#### listing_styles
```python
listing_styles = db.Table('listing_styles',
    db.Column('listing_uuid', db.String(36), db.ForeignKey('listings.uuid'), primary_key=True),
    db.Column('style_uuid', db.String(36), db.ForeignKey('styles.uuid'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
```

---

## Data Extraction Strategy

### Phase 1: Basic Listing Data (No Extra API Calls)
From `/users/{username}/inventory` response:

```python
def extract_from_listing_response(listing_data: Dict) -> Dict:
    """Extract what we need from basic inventory API response."""
    release = listing_data.get('release', {})
    
    return {
        # Core listing data
        'listing_id': str(listing_data['id']),
        'release_id': str(release['id']),
        'status': listing_data['status'],
        'media_condition': listing_data['condition'],
        'sleeve_condition': listing_data['sleeve_condition'],
        'price': listing_data['price']['value'],
        'currency': listing_data['price']['currency'],
        'quantity': listing_data.get('quantity', 1),
        'location': listing_data.get('location', ''),
        'external_id': listing_data.get('external_id', ''),
        'comments': listing_data.get('comments', ''),
        'posted_at': parse_datetime(listing_data['posted']),
        
        # Release display data
        'release_title': release['title'],
        'release_year': release.get('year'),
        'image_uri': extract_primary_image(release['images']),
        'catalog_number': release.get('catalog_number', ''),
        
        # Artist/Label names for lookup
        'artist_name': release['artist'],
        'label_name': release['label'],
        'format_string': release.get('format', '')
    }
```

### Phase 2: Enriched Data (Optional, Cached)
From `/releases/{release_id}` response:

```python
def enrich_from_release_details(release_id: str) -> Dict:
    """Fetch additional data from release endpoint (cached)."""
    response = fetch_release_details(release_id)
    
    return {
        'genres': response.get('genres', []),           # ["Electronic", "Jazz"]
        'styles': response.get('styles', []),           # ["House", "Deep House"]
        'artists_detailed': response.get('artists', []), # Full artist objects with IDs
        'labels_detailed': response.get('labels', []),   # Full label objects with IDs
        'tracklist': response.get('tracklist', [])
    }
```

---

## API Call Optimization Strategy

### Current Approach (Inefficient)
```
Sync = 100 listings × 1 page call = ~5-10 API calls
Total: 5-10 calls per sync
```

### Proposed Approach

#### Option 1: Lazy Genre/Style Enrichment
```
Initial Sync: 1 CSV export call (all listings)
Background Job: 100 listings × 1 release detail call (once)
  → Cache for 30 days
  → Only for unique release_id values (dedupe)
  
Total: 1 + ~50 unique releases = 51 calls (one-time)
```

#### Option 2: On-Demand Enrichment
```
Initial Sync: 1 CSV export call (all listings)
Detail View: Fetch genres/styles when user clicks listing
  → Cache indefinitely
  → Only fetch once per release_id
  
Total: 1 + as needed
```

#### Option 3: Batch Enrichment (Recommended)
```
Initial Sync: 1 CSV export call (all listings)
Hourly Job: Find releases missing genres/styles
  → Batch fetch 60 releases per hour (rate limit friendly)
  → Cache forever
  → Within 2-3 days, all releases enriched
  
Total: 1 + (unique_releases / 60) over time
```

---

## Field Reduction Summary

### Before (Current Model)
- **Total Fields**: ~50 fields
- **Redundant Data**: Artist/label names duplicated
- **Stale Data**: Community stats, timestamps
- **Unused Fields**: Barcodes, master URLs, etc.
- **API Calls**: Multiple per sync

### After (Proposed Model)
- **Total Fields**: ~23 fields in Listing
- **Normalized**: Artist/Label in separate tables
- **Fresh When Needed**: Fetch community stats on-demand
- **Essential Only**: Only fields used in UI
- **API Calls**: 1 CSV export + background enrichment

---

## Migration Impact

### Immediate Benefits
- ✅ 50% fewer fields to sync
- ✅ Cleaner data model
- ✅ Easier to query
- ✅ Less storage

### Phase 1 (Hash + Soft Delete)
- No schema change needed
- Works with current model

### Phase 2 (CSV Export)
- No schema change needed
- Works with current model

### Phase 3 (Field Reduction)
- **Migration Required**: Drop unused columns
- **Risk**: Low (data not used)
- **Rollback**: Easy (re-add columns)

### Phase 4 (Normalization)
- **Migration Required**: Add Artist/Label/Genre/Style tables
- **Risk**: Low (hybrid approach)
- **Rollback**: Easy (remove FK constraints)

---

## Recommended Implementation Order

### Week 1-2: Foundation
1. Add `content_hash`, `is_active`, `removed_at` to Listing
2. Implement hash-based change detection
3. Implement soft deletes
4. Add CSV export sync

### Week 3: Field Cleanup
1. Create migration to drop unused fields
2. Test with reduced model
3. Validate all UI still works

### Week 4: Normalization
1. Create Artist, Label, Genre, Style tables
2. Add foreign keys to Listing
3. Keep denormalized fields (hybrid)
4. Background job to populate relationships

### Week 5+: Enrichment
1. Background job to fetch genres/styles
2. Cache release details
3. Admin UI to manage artists/labels
4. Merge duplicate artists

---

## Questions to Answer

- [ ] Do you need to display genres/styles in the list view? (affects sync strategy)
- [ ] How important is artist/label search? (affects indexing strategy)  
- [ ] Should we fetch release details for all listings upfront? (affects API usage)
- [ ] Do you want to manually curate artist/label descriptions? (affects schema)
- [ ] Keep `external_id` and `location` fields? (your custom inventory fields)

---

## UI Field Usage Analysis

### ✅ Fields Actually Displayed in UI

#### Main List View (collage)
- `image_uri` - Primary vinyl image
- `release_title` - Album/release name
- `primary_artist` (or `artist_names`) - Artist name
- `price_value` - Price display

#### Detail View
- `image_uri` - Large vinyl image
- `release_title` - Album title
- `artist_names` - Artist display
- `price_value` - Price display
- `label_names` - Label display
- `release_year` - Year display
- `condition` - Media condition
- `sleeve_condition` - Sleeve condition
- `comments` - Seller notes

#### Search/Filter Parameters
- `q` - Text search (searches `release_title` and `artist_names`)
- `artist` - Artist filter
- **`genre`** - **Genre filter (USED IN API)**
- `format` - Format filter
- `label` - Label filter
- `year` - Year filter
- `condition` - Condition filter
- `sleeve_condition` - Sleeve condition filter

### ❌ Fields NOT Used Anywhere in UI

- `location` - Only in database, never displayed
- `external_id` - Only in database, never displayed
- `genres` - **IN DATABASE, USED IN SEARCH, BUT NOT DISPLAYED**
- `styles` - Not used at all
- `weight` - Not displayed
- `shipping_price` - Not displayed (flat rate used)
- `barcode` - Not displayed
- `catalog_number` - Not displayed
- `master_id` / `master_url` - Not displayed
- `release_community_have/want` - Not displayed
- All URL construction fields (`uri`, `resource_url`, etc.)

### 🔍 Key Finding: Genre is Used!

**Important Discovery**: 
```python
# app/routes/api.py (line 57-63)
genre = request.args.get('genre')
data = service.search_items(
    query=query,
    artist=artist,
    genre=genre,  # ← Genre filtering IS implemented
    format_type=format_type
)

# app/services/inventory_service.py (line 81)
if genre:
    q = q.filter(Listing.genres.ilike(f'%{genre}%'))
```

**BUT**: Genre filter UI is not visible in templates yet! This is backend-ready but frontend-incomplete.

---

## Metadata Field Strategy Analysis

### Option 1: JSON metadata Column
Store genres, styles, location, and future fields in a flexible JSON column:

```python
class Listing(db.Model):
    metadata = db.Column(db.JSON, nullable=True)
    
    # Example structure:
    # {
    #   "genres": ["Electronic", "Jazz"],
    #   "styles": ["House", "Deep House", "Ambient"],
    #   "location": "CB1",
    #   "weight": 230.0,
    #   "catalog_number": "20 B2",
    #   "barcode": "123456789",
    #   "external_id": "Colin purchased from Bandcamp"
    # }
```

#### ✅ Pros
- **Flexible**: Add new fields without migrations
- **Clean**: Keeps main table focused on core fields
- **Future-proof**: Can add arbitrary data later
- **Easy to extend**: No schema changes needed

#### ⚠️ Cons & Pitfalls
1. **No Indexing**: Cannot index JSON fields efficiently in SQLite
   - Genre search would require full table scan
   - **CRITICAL**: Your genre filter would become VERY slow
   
2. **No Type Safety**: JSON values can be any type
   - Easy to introduce data inconsistencies
   - No database-level validation
   
3. **Complex Queries**: Searching JSON in SQL is painful
   ```python
   # This is slow and database-specific:
   q = q.filter(Listing.metadata['genres'].contains('Electronic'))
   ```

4. **Migration Pain**: Moving data to normalized tables later is hard
   - Need to parse JSON for every record
   - Risk of data loss if JSON structure inconsistent

5. **No Foreign Keys**: Can't create relationships
   - Genre normalization becomes impossible
   - Can't count listings per genre efficiently

### Option 2: Hybrid Approach (Recommended)

Keep searchable fields as columns, use metadata for truly optional data:

```python
class Listing(db.Model):
    # Searchable/filterable (indexed columns)
    genres = db.Column(db.String(500), index=True)  # Keep indexed!
    styles = db.Column(db.String(500), index=True)  # Keep indexed!
    
    # Non-searchable metadata (JSON)
    metadata = db.Column(db.JSON, nullable=True)
    # {
    #   "location": "CB1",
    #   "weight": 230.0,
    #   "barcode": "123456789",
    #   "external_id": "Colin purchased...",
    #   "custom_notes": "...",
    #   "future_field": "..."
    # }
```

#### ✅ Why This Works
- Genres/styles remain searchable and fast
- Non-searchable data flexible and extensible
- Clear separation of concerns
- Easy to add normalized Genre/Style tables later

### Option 3: Separate Extension Table

Create a one-to-one extension table for optional metadata:

```python
class Listing(db.Model):
    # Core fields only
    pass

class ListingMetadata(db.Model):
    listing_uuid = db.Column(db.String(36), db.ForeignKey('listings.uuid'), primary_key=True)
    location = db.Column(db.String(50))
    external_id = db.Column(db.String(100))
    weight = db.Column(db.Float)
    barcode = db.Column(db.String(100))
    catalog_number = db.Column(db.String(100))
    custom_data = db.Column(db.JSON)  # For truly unknown future fields
```

#### ✅ Pros
- Clean separation
- Main table stays small and fast
- Can add indexes on metadata fields
- Easy to query both tables

#### ⚠️ Cons
- Requires JOIN for metadata access
- More complex queries
- Migration needed for new fields

---

## Final Recommendation: Hybrid + Normalization Path

### Phase 1: Keep Current Structure + Add Optimizations
```python
class Listing(db.Model):
    # Keep indexed for search/filter
    genres = db.Column(db.String(500), index=True)
    styles = db.Column(db.String(500), index=True)
    
    # Keep for your inventory management
    location = db.Column(db.String(50))
    external_id = db.Column(db.String(100))
    
    # Add optimization fields
    content_hash = db.Column(db.String(64), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Add optional metadata for extensibility
    metadata = db.Column(db.JSON, nullable=True)
```

### Phase 2: Normalize Genres/Styles (Week 4+)
```python
class Genre(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)

class Style(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    genre_id = db.Column(db.String(36), db.ForeignKey('genres.uuid'))

# Many-to-many relationships
listing_genres = db.Table('listing_genres', ...)
listing_styles = db.Table('listing_styles', ...)

class Listing(db.Model):
    # Keep denormalized for backward compatibility
    genres = db.Column(db.String(500))  # "Electronic; Jazz"
    styles = db.Column(db.String(500))  # "House; Deep House"
    
    # Add normalized relationships
    genre_list = db.relationship('Genre', secondary='listing_genres')
    style_list = db.relationship('Style', secondary='listing_styles')
```

### Migration Path
```python
# Background job to populate normalized tables
def enrich_genres_styles():
    for listing in Listing.query.filter_by(genre_list=None):
        # Parse semicolon-separated string
        genre_names = listing.genres.split(';') if listing.genres else []
        
        for genre_name in genre_names:
            genre = get_or_create_genre(genre_name.strip())
            listing.genre_list.append(genre)
        
        # Same for styles
        style_names = listing.styles.split(';') if listing.styles else []
        for style_name in style_names:
            style = get_or_create_style(style_name.strip())
            listing.style_list.append(style)
        
    db.session.commit()
```

---

## Genre/Style Data Enrichment Strategy

Since genres/styles require additional API calls to `/releases/{id}`:

### Recommended: Lazy Background Enrichment

```python
@celery.task
def enrich_release_genres_styles(release_id: str):
    """Fetch and cache genre/style data for a release."""
    
    # Check if already enriched
    listing = Listing.query.filter_by(release_id=release_id).first()
    if listing.genres:
        return  # Already has data
    
    # Fetch from Discogs API
    response = fetch_release_details(release_id)
    
    genres = response.get('genres', [])
    styles = response.get('styles', [])
    
    # Update all listings with this release_id
    Listing.query.filter_by(release_id=release_id).update({
        'genres': '; '.join(genres),
        'styles': '; '.join(styles)
    })
    
    db.session.commit()

# Run hourly: enrich 60 releases (within rate limits)
@celery.beat_schedule('0 * * * *')
def hourly_enrichment():
    unenriched = Listing.query.filter(
        Listing.genres.is_(None)
    ).limit(60).all()
    
    for listing in unenriched:
        enrich_release_genres_styles.delay(listing.release_id)
```

**Timeline**: 500 listings ÷ 60 per hour = ~8 hours to full enrichment

---

## Updated Field Count

### Current Model: ~50 fields
### Minimal Model: ~25 fields

| Category | Current | Proposed | Notes |
|----------|---------|----------|-------|
| Core Listing | 12 | 12 | Keep all |
| Display | 8 | 6 | Remove redundant URLs |
| Search/Filter | 8 | 6 | Keep genres/styles/artist/label |
| Inventory | 4 | 4 | Keep location/external_id |
| Stats | 2 | 0 | Remove community stats |
| URLs | 8 | 1 | Keep image_uri only |
| Metadata | 0 | 1 | New JSON field |
| Optimization | 2 | 4 | Add hash/soft delete |
| **Total** | **~50** | **~25** | **50% reduction** |

---

## Next Steps

1. ✅ **Confirmed**: Keep `genres` and `styles` as indexed columns (used in search)
2. ✅ **Confirmed**: Keep `location` and `external_id` (your inventory fields)
3. ✅ **Confirmed**: Add `metadata` JSON column for future extensibility
4. **Decision Needed**: Implement genre/style enrichment now or later?
5. **Decision Needed**: Drop unused fields (community stats, URLs) now or later?

---

**Last Updated**: 2025-10-14  
**Status**: Updated with UI analysis - Awaiting Review
