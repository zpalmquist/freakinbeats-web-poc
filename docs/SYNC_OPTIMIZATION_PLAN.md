# Discogs Sync Optimization Migration Plan

## Overview

This document outlines the migration plan to optimize the Discogs synchronization service, eliminating the inefficient "iterate over every listing" approach and implementing modern caching and change detection strategies.

## Current Issues

- **Inefficient Iteration**: Loops through 100+ listings every sync (hourly!)
- **Excessive API Calls**: Multiple paginated requests per sync
- **Destructive Updates**: Deletes and recreates listings, risking data loss
- **No Change Detection**: Updates records even when nothing changed
- **Blocking Normalization**: Can't safely add Artist/Label tables

## Migration Strategy

### Phase 1: Foundation (Week 1)
**Goal**: Implement core optimizations without breaking existing functionality

#### 1.1 Add Content Hash Change Detection
**Priority**: CRITICAL  
**Effort**: Low  
**Risk**: Minimal

**Changes Needed**:
```python
# app/models/listing.py
class Listing(db.Model):
    # Add new field
    content_hash = db.Column(db.String(64), index=True)
```

**Migration**:
```bash
alembic revision -m "add_content_hash_to_listings"
alembic upgrade head
```

**Benefits**:
- O(1) change detection
- Skip 80-90% of unchanged listings
- Instant sync for stable inventory

**Implementation**:
- Add `calculate_hash()` helper function
- Hash key fields: price, condition, status, quantity
- Compare hash before updating

---

#### 1.2 Replace Hard Deletes with Soft Deletes
**Priority**: CRITICAL  
**Effort**: Low  
**Risk**: Minimal

**Changes Needed**:
```python
# app/models/listing.py
class Listing(db.Model):
    # Add new field
    is_active = db.Column(db.Boolean, default=True, index=True)
    removed_at = db.Column(db.DateTime, nullable=True)
```

**Migration**:
```bash
alembic revision -m "add_soft_delete_to_listings"
alembic upgrade head
```

**Benefits**:
- Never lose historical data
- Can restore accidentally removed listings
- Safer for future normalized relationships
- Analytics on sold/removed items

**Implementation**:
- Change `db.session.delete()` to `listing.is_active = False`
- Update all queries to filter `is_active=True` by default
- Add cleanup job for old inactive records (optional)

---

#### 1.3 Implement Bulk Operations
**Priority**: HIGH  
**Effort**: Medium  
**Risk**: Low

**Changes Needed**:
```python
# app/services/discogs_sync_service.py
def sync_all_listings(self):
    # Replace individual operations with bulk
    db.session.bulk_insert_mappings(Listing, new_listings)
    db.session.bulk_update_mappings(Listing, updated_listings)
```

**Benefits**:
- 10-50x faster database operations
- Single transaction for all changes
- Reduced lock contention

**Implementation**:
- Collect new/updated listings in lists
- Use SQLAlchemy bulk operations
- Maintain single commit at end

---

### Phase 2: CSV Export Integration (Week 2)
**Goal**: Replace paginated API calls with single export request

#### 2.1 Add CSV Export Endpoint Support
**Priority**: HIGH  
**Effort**: Medium  
**Risk**: Low

**New Method**:
```python
def sync_via_csv_export(self) -> Dict[str, int]:
    """Download complete inventory as CSV in single request."""
    url = f"{self.base_url}/users/{self.seller_username}/inventory/export"
    response = requests.get(url, headers=self.headers, timeout=60)
    
    # Parse CSV
    # Bulk process all listings
    # Return stats
```

**Benefits**:
- 1 API call instead of 5-20 paginated requests
- Faster processing (CSV parsing vs JSON)
- Lower rate limit consumption
- Complete atomic snapshot

**Migration Path**:
- Implement new method alongside existing
- Add feature flag: `USE_CSV_EXPORT=true`
- Test thoroughly on staging
- Gradually roll out to production

---

### Phase 3: Caching Layer (Week 3)
**Goal**: Reduce redundant API calls and enable faster responses

#### 3.1 Add Redis Caching
**Priority**: MEDIUM  
**Effort**: Medium  
**Risk**: Low

**Dependencies**:
```bash
pip install redis
```

**Configuration**:
```python
# config.py
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour default
```

**Implementation**:
```python
# app/services/discogs_sync_service.py
import redis
import json

class DiscogsSyncService:
    def __init__(self):
        self.redis = redis.from_url(current_app.config['REDIS_URL'])
        self.cache_ttl = current_app.config['CACHE_TTL']
    
    def _fetch_with_cache(self, key: str, fetch_func):
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        data = fetch_func()
        self.redis.setex(key, self.cache_ttl, json.dumps(data))
        return data
```

**Benefits**:
- Instant responses for cached data
- Reduced API calls during high traffic
- Configurable freshness (TTL)
- Shared cache across multiple instances

**Optional**: Can skip if single-server deployment

---

### Phase 4: Normalized Tables (Week 4)
**Goal**: Safely add Artist/Label normalization with new sync strategy

#### 4.1 Add Artist and Label Tables
**Priority**: MEDIUM  
**Effort**: High  
**Risk**: Low (with new sync strategy)

**Migration**:
```bash
alembic revision -m "add_artist_and_label_tables"
alembic upgrade head
```

**Implementation Strategy**:
```python
# Hybrid approach - keep both denormalized and normalized
class Listing(db.Model):
    # Keep existing for search/display (denormalized)
    artist_names = db.Column(db.Text)
    primary_artist = db.Column(db.String(255))
    
    # Add normalized relationship (optional enrichment)
    artist_id = db.Column(db.String(36), db.ForeignKey('artists.uuid'), nullable=True)
    artist = db.relationship('Artist')
```

**Background Enrichment Job**:
```python
@celery.task
def enrich_artist_relationships():
    """Background job to populate artist_id from artist_names."""
    listings_without_artist = Listing.query.filter_by(artist_id=None).limit(100)
    
    for listing in listings_without_artist:
        artist = get_or_create_artist(listing.primary_artist)
        listing.artist_id = artist.uuid
    
    db.session.commit()
```

**Benefits**:
- Gradual migration (doesn't break sync)
- Best of both worlds (speed + normalization)
- Can enhance artist data over time
- No risk to current functionality

---

### Phase 5: Advanced Features (Future)
**Goal**: Additional optimizations for scale

#### 5.1 Background Job Queue (Celery)
**When**: > 1000 listings or multiple workers needed  
**Effort**: High  
**Benefits**: Async processing, retry logic, progress tracking

#### 5.2 Delta Sync with Timestamps
**When**: Discogs adds `modified_since` filter to API  
**Effort**: Low  
**Benefits**: Only fetch changed records

#### 5.3 Event-Driven Webhooks
**When**: Real-time updates needed  
**Effort**: High  
**Benefits**: Instant sync on listing changes

---

## Implementation Timeline

### Week 1: Foundation
- [ ] Day 1-2: Add content_hash field + migration
- [ ] Day 2-3: Implement hash calculation in sync
- [ ] Day 3-4: Add soft delete fields + migration
- [ ] Day 4-5: Replace hard deletes with soft deletes
- [ ] Day 5: Testing and validation

**Deliverable**: 80-90% faster sync with safe deletes

### Week 2: CSV Export
- [ ] Day 1-2: Implement CSV export method
- [ ] Day 2-3: Add CSV parsing logic
- [ ] Day 3-4: Integration with bulk operations
- [ ] Day 4-5: A/B testing vs current method

**Deliverable**: Single API call sync option

### Week 3: Caching
- [ ] Day 1: Setup Redis instance
- [ ] Day 2-3: Implement cache layer
- [ ] Day 3-4: Add cache invalidation logic
- [ ] Day 4-5: Performance testing

**Deliverable**: Optional Redis caching

### Week 4: Normalization
- [ ] Day 1-2: Create Artist/Label models + migration
- [ ] Day 2-3: Add foreign key relationships to Listing
- [ ] Day 3-4: Implement background enrichment job
- [ ] Day 4-5: Testing and gradual rollout

**Deliverable**: Normalized schema ready

---

## Rollback Plan

Each phase is designed to be independently reversible:

### Phase 1 Rollback
```bash
alembic downgrade -1  # Revert migration
git revert <commit>   # Revert code changes
```

### Phase 2 Rollback
```bash
# Toggle feature flag
export USE_CSV_EXPORT=false
# Falls back to paginated sync
```

### Phase 3 Rollback
```bash
# Remove Redis from requirements
pip uninstall redis
# Code gracefully handles missing Redis
```

### Phase 4 Rollback
```bash
alembic downgrade -1  # Remove Artist/Label tables
# Listings continue working with denormalized fields
```

---

## Success Metrics

### Phase 1
- **Before**: 100+ listings × 100ms = 10+ seconds sync time
- **After**: 10-20 changed listings × 100ms = 1-2 seconds sync time
- **Target**: 80% reduction in sync time

### Phase 2
- **Before**: 5-20 API calls per sync
- **After**: 1 API call per sync
- **Target**: 95% reduction in API calls

### Phase 3
- **Before**: Every request hits API
- **After**: 90% cache hit rate
- **Target**: 10x faster repeat queries

### Phase 4
- **Before**: No artist management possible
- **After**: Curated artist database
- **Target**: 100% listings enriched within 24 hours

---

## Risk Mitigation

### Data Loss Prevention
- ✅ Soft deletes preserve all data
- ✅ Content hash tracks what changed
- ✅ Audit log of all sync operations
- ✅ Database backups before migrations

### Performance Monitoring
- ✅ Log sync duration for each phase
- ✅ Track API call count
- ✅ Monitor cache hit rates
- ✅ Alert on sync failures

### Gradual Rollout
- ✅ Feature flags for each phase
- ✅ A/B testing new vs old methods
- ✅ Canary deployments (5% → 50% → 100%)
- ✅ Easy rollback mechanisms

---

## Configuration Changes

### Environment Variables
```bash
# Phase 1 - No new config needed

# Phase 2
USE_CSV_EXPORT=true  # Enable CSV export sync

# Phase 3
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# Phase 4
ENABLE_ARTIST_ENRICHMENT=true
ENRICHMENT_BATCH_SIZE=100
```

### Dependencies
```bash
# requirements.txt additions

# Phase 3
redis>=5.0.0

# Phase 5 (future)
celery>=5.3.0  # If async jobs needed
```

---

## Testing Strategy

### Unit Tests
- Hash calculation correctness
- Soft delete query filtering
- Bulk operation accuracy
- CSV parsing edge cases

### Integration Tests
- Full sync with test data
- Cache invalidation scenarios
- Concurrent sync handling
- Rollback procedures

### Performance Tests
- Benchmark current vs optimized
- Load testing with 1000+ listings
- Cache hit rate validation
- Memory usage profiling

---

## Documentation Updates

### README.md
- Update sync strategy description
- Add Redis setup instructions (Phase 3)
- Document new environment variables

### API Documentation
- No external API changes needed
- Internal sync API remains compatible

### Runbook
- New troubleshooting for cache issues
- Soft delete cleanup procedures
- Artist enrichment monitoring

---

## Next Steps

1. **Review this plan** with team
2. **Create Jira tickets** for each phase
3. **Setup staging environment** for testing
4. **Week 1 kickoff**: Begin Phase 1 implementation
5. **Weekly retros**: Adjust plan based on learnings

---

## Questions to Answer Before Starting

- [ ] Do we have Redis available? (Phase 3)
- [ ] What's our rollback SLA requirement?
- [ ] Should we keep old sync method as fallback?
- [ ] How long to retain soft-deleted records?
- [ ] Who approves migrations to production?

---

## Additional Resources

- [Discogs API Documentation](https://www.discogs.com/developers)
- [SQLAlchemy Bulk Operations](https://docs.sqlalchemy.org/en/14/orm/persistence_techniques.html#bulk-operations)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Redis Python Client](https://redis-py.readthedocs.io/)

---

**Last Updated**: 2025-10-14  
**Owner**: Engineering Team  
**Status**: Draft - Awaiting Approval
