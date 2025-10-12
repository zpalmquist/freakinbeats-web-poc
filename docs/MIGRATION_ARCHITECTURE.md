# 🔄 SQLAlchemy ORM with Discogs API Integration

## Overview

The Freakinbeats web application has been migrated from a CSV-based system to a robust SQLAlchemy ORM architecture with automatic Discogs API synchronization. The system now features:

- **SQLite Database**: All listings stored in a local SQLite database
- **Automatic Sync**: Hourly synchronization with Discogs API
- **RESTful API**: Enhanced API endpoints with search and filtering
- **Scheduled Tasks**: APScheduler for automated updates

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────────┐             │
│  │   Routes     │         │    Services      │             │
│  │  (API/Main)  │────────▶│  - Inventory     │             │
│  └──────────────┘         │  - Discogs Sync  │             │
│                           └──────────────────┘             │
│                                    │                         │
│                                    ▼                         │
│                           ┌──────────────────┐             │
│                           │  SQLAlchemy ORM  │             │
│                           │   (Models)       │             │
│                           └──────────────────┘             │
│                                    │                         │
└────────────────────────────────────┼─────────────────────────┘
                                     ▼
                            ┌──────────────────┐
                            │  SQLite Database │
                            │  (freakinbeats.db)│
                            └──────────────────┘
                                     ▲
                                     │
                            ┌──────────────────┐
                            │  APScheduler     │
                            │  (Hourly Sync)   │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Discogs API     │
                            │  (External)      │
                            └──────────────────┘
```

## Key Components

### 1. Database Models (`app/models/listing.py`)

The `Listing` model represents a Discogs marketplace listing with all relevant fields:

- **Listing Information**: ID, status, condition, posted date
- **Pricing**: Price value, currency, shipping costs
- **Release Details**: Title, year, artist, label, format
- **Media Information**: Genre, style, catalog number, images
- **Statistics**: Community have/want counts
- **Timestamps**: Created/updated tracking

### 2. Discogs Sync Service (`app/services/discogs_sync_service.py`)

Handles all interaction with the Discogs API:

- **Fetches listings** from seller inventory endpoint
- **Rate limiting** to respect API limits (1 request/second)
- **Error handling** for authentication, network issues
- **Data transformation** from API format to database schema
- **Smart sync** that adds, updates, and removes listings

### 3. Inventory Service (`app/services/inventory_service.py`)

Provides database access for the application:

- `get_all_items()`: Retrieve all listings
- `get_item_by_listing_id()`: Get specific listing
- `search_items()`: Search with filters (query, artist, genre, format)
- `get_stats()`: Get inventory statistics

### 4. Scheduled Sync (`app/__init__.py`)

APScheduler integration for automatic updates:

- Runs **initial sync** on application startup
- Schedules **hourly sync** job (configurable)
- Executes in **background thread**
- Logs all sync operations and statistics

## Configuration

All configuration is in `config.py`:

### Database Settings

```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///freakinbeats.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Discogs API Settings

```python
DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')  # Required
DISCOGS_SELLER_USERNAME = 'freakin_beats'
DISCOGS_USER_AGENT = 'FreakinbeatsWebApp/1.0'
```

### Scheduler Settings

```python
SYNC_INTERVAL_HOURS = 1  # Sync every hour
ENABLE_AUTO_SYNC = True  # Enable/disable auto-sync
```

## Environment Variables

Set these environment variables before running:

```bash
# Required for API sync
export DISCOGS_TOKEN="your_discogs_api_token"

# Optional (with defaults)
export DISCOGS_SELLER_USERNAME="freakin_beats"
export ENABLE_AUTO_SYNC="true"
export DATABASE_URL="sqlite:///freakinbeats.db"
```

## Getting Started

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

The new requirements include:
- `Flask-SQLAlchemy==3.1.1`
- `APScheduler==3.10.4`
- `requests==2.31.0`

### 2. Set Environment Variables

```bash
export DISCOGS_TOKEN="your_token_here"
export DISCOGS_SELLER_USERNAME="your_seller_username"
```

Get your Discogs token from: https://www.discogs.com/settings/developers

### 3. Migrate Existing CSV Data (Optional)

If you have existing CSV data:

```bash
python3 migrate_csv_to_db.py
```

Options:
- `--csv-file path/to/file.csv`: Specify custom CSV file
- `--clear-db`: Clear database before import

### 4. Start the Application

```bash
python3 run.py
```

Or use the start script:

```bash
./start_server.sh
```

The application will:
1. Create database tables (if not exist)
2. Run initial sync with Discogs API
3. Schedule hourly sync jobs
4. Start the Flask web server

## API Endpoints

The application now provides enhanced API endpoints:

### Get All Listings
```
GET /api/data
```

Returns all listings, sorted by posted date (newest first).

### Get Specific Listing
```
GET /api/data/<listing_id>
```

Returns a single listing by its Discogs listing ID.

### Search Listings
```
GET /api/search?q=artist&artist=beatles&genre=rock&format=vinyl
```

Query parameters:
- `q`: Search query (searches title and artist)
- `artist`: Filter by artist name
- `genre`: Filter by genre
- `format`: Filter by format type

### Get Statistics
```
GET /api/stats
```

Returns inventory statistics:
```json
{
  "total_listings": 538,
  "last_updated": "2025-10-10T12:00:00"
}
```

## Sync Process

### Initial Sync

On application startup, if `DISCOGS_TOKEN` is configured:

1. Connects to Discogs API
2. Fetches all seller listings (paginated)
3. Compares with existing database records
4. Adds new listings, updates existing, removes deleted
5. Logs statistics

### Scheduled Sync

Every hour (or configured interval):

1. APScheduler triggers sync job
2. Sync service fetches latest data from Discogs
3. Database is updated with changes
4. Results are logged

### Manual Sync

You can trigger a manual sync by:

1. Restarting the application (runs initial sync)
2. Using the migration script with fresh CSV data
3. Creating a custom admin endpoint (future enhancement)

## Database Schema

The `listings` table includes:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| listing_id | VARCHAR(50) | Discogs listing ID (unique) |
| status | VARCHAR(50) | Listing status |
| condition | VARCHAR(50) | Media condition |
| sleeve_condition | VARCHAR(50) | Sleeve condition |
| posted | VARCHAR(100) | Posted date |
| price_value | FLOAT | Price amount |
| price_currency | VARCHAR(10) | Price currency |
| release_id | VARCHAR(50) | Discogs release ID |
| release_title | VARCHAR(500) | Release title |
| artist_names | VARCHAR(500) | All artists |
| primary_artist | VARCHAR(255) | Main artist |
| genres | VARCHAR(500) | Genres |
| styles | VARCHAR(500) | Styles |
| image_uri | VARCHAR(500) | Cover image URL |
| created_at | DATETIME | Record created |
| updated_at | DATETIME | Record updated |
| ... | ... | (30+ more fields) |

## Monitoring and Logging

The application logs all sync activities:

```
[INFO] Database tables created
[INFO] Scheduler started. Sync interval: 1 hour(s)
[INFO] Running initial Discogs sync...
[INFO] Starting sync for seller: freakin_beats
[DEBUG] Fetching page 1...
[DEBUG] Page 1: 100 listings (Total: 100)
[INFO] Total listings fetched: 538
[INFO] Sync completed: 15 added, 520 updated, 3 removed
```

## Error Handling

The system includes comprehensive error handling:

- **Authentication Errors**: Logs warning if token is invalid
- **Rate Limits**: Automatically waits and retries
- **Network Errors**: Logs errors and continues operation
- **Database Errors**: Rolls back transactions on failure

## Performance

- **Initial sync**: ~30-60 seconds (depending on inventory size)
- **Hourly sync**: ~30-60 seconds
- **Database queries**: Optimized with indexes on key fields
- **Memory footprint**: Minimal (SQLite is embedded)

## Troubleshooting

### No listings appearing

1. Check if `DISCOGS_TOKEN` is set
2. Verify token is valid at Discogs settings
3. Check application logs for errors
4. Ensure seller username is correct

### Sync not running

1. Verify `ENABLE_AUTO_SYNC=true`
2. Check that `DISCOGS_TOKEN` is set
3. Review logs for scheduler startup messages

### Database errors

1. Delete `freakinbeats.db` and restart (recreates database)
2. Run migration script to reimport data
3. Check file permissions on database file

### API rate limits

The sync service automatically handles rate limits:
- Sleeps 1 second between requests
- Waits 60 seconds on rate limit errors
- Retries failed requests

## Migration from CSV

The old CSV-based system is fully replaced. Benefits:

| CSV System | SQLAlchemy System |
|------------|-------------------|
| Manual CSV updates | Automatic hourly sync |
| File I/O overhead | Fast database queries |
| No search/filter | Advanced search API |
| Static data | Real-time updates |
| Single file dependency | Scalable database |

## Future Enhancements

Potential improvements:

1. **Admin Dashboard**: Web UI for manual sync and monitoring
2. **PostgreSQL Support**: For production deployments
3. **Webhook Integration**: Real-time updates via Discogs webhooks
4. **Caching Layer**: Redis for frequently accessed data
5. **Analytics**: Track listing views, sales, trends
6. **Multi-seller Support**: Aggregate multiple seller accounts

## Development

### Running Tests

```bash
# Install test dependencies
pip3 install pytest pytest-flask

# Run tests
pytest
```

### Database Migrations

For schema changes, use Flask-Migrate:

```bash
pip3 install Flask-Migrate
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### Debugging Sync

To test sync without waiting:

```python
from app import create_app
from app.services.discogs_sync_service import DiscogsSyncService

app = create_app()
with app.app_context():
    sync = DiscogsSyncService(
        token='your_token',
        seller_username='your_username',
        user_agent='Test/1.0'
    )
    stats = sync.sync_all_listings()
    print(stats)
```

## Support

For issues or questions:

1. Check the logs for error messages
2. Review this documentation
3. Verify environment variables are set correctly
4. Ensure dependencies are installed

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

