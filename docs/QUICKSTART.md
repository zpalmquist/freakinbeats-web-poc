# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Get Your Discogs Token

1. Go to https://www.discogs.com/settings/developers
2. Click "Generate new token"
3. Copy the token

### Step 2: Install Dependencies

```bash
cd freakinbeats-web-poc
pip3 install -r requirements.txt
```

### Step 3: Configure Environment

Set your Discogs credentials:

```bash
export DISCOGS_TOKEN="your_token_here"
export DISCOGS_SELLER_USERNAME="your_seller_username"
```

Or create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 4: Start the Application

```bash
python3 run.py
```

Or use the start script:

```bash
./start_server.sh
```

### Step 5: Access the Application

Open your browser to:
```
http://localhost:3000
```

## What Happens on Startup?

1. ✅ Creates database tables (if needed)
2. ✅ Performs initial sync with Discogs API
3. ✅ Schedules hourly sync jobs
4. ✅ Starts web server on port 3000

## First Run Example

```bash
$ export DISCOGS_TOKEN="your_token"
$ export DISCOGS_SELLER_USERNAME="freakin_beats"
$ python3 run.py

[INFO] Database tables created
[INFO] Scheduler started. Sync interval: 1 hour(s)
[INFO] Running initial Discogs sync...
[INFO] Starting sync for seller: freakin_beats
[DEBUG] Fetching page 1...
[DEBUG] Page 1: 100 listings (Total: 100)
[DEBUG] Fetching page 2...
[DEBUG] Page 2: 100 listings (Total: 200)
...
[INFO] Total listings fetched: 538
[INFO] Sync completed: 538 added, 0 updated, 0 removed
[INFO] Initial sync completed: {'added': 538, 'updated': 0, 'removed': 0, 'total': 538}
 * Running on http://127.0.0.1:3000
```

## Migrating Existing CSV Data

If you already have CSV data in the `ingest/` directory:

```bash
python3 migrate_csv_to_db.py
```

This will import all CSV data into the database.

## Verifying the Setup

### Check the API

```bash
# Get all listings
curl http://localhost:3000/api/data

# Get statistics
curl http://localhost:3000/api/stats

# Search for an artist
curl "http://localhost:3000/api/search?artist=beatles"
```

### Check the Database

```bash
# View database file
ls -lh freakinbeats.db

# Query database
sqlite3 freakinbeats.db "SELECT COUNT(*) FROM listings;"
```

## Common Issues

### Issue: "DISCOGS_TOKEN not set"

**Solution**: Make sure to export the environment variable:
```bash
export DISCOGS_TOKEN="your_actual_token"
```

### Issue: "No listings fetched from API"

**Possible causes**:
1. Invalid token
2. Wrong seller username
3. Seller has no listings
4. Network issues

**Solution**: Check your token and username at Discogs settings.

### Issue: Port 3000 already in use

**Solution**: Stop any existing server:
```bash
lsof -ti:3000 | xargs kill -9
```

Or change the port in `config.py`:
```python
PORT = 3001
```

## Next Steps

- 📖 Read `MIGRATION_ARCHITECTURE.md` for detailed documentation
- 🎨 Customize styles in `app/static/scss/`
- 🔧 Modify sync interval in `config.py`
- 📊 View logs for sync status
- 🌐 Build your custom frontend

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

The scheduler will automatically shut down gracefully.

## Troubleshooting

Enable debug logging:

```bash
export FLASK_DEBUG=true
python3 run.py
```

Check the console output for detailed information about:
- Database operations
- API requests
- Sync statistics
- Error messages

## Support

For detailed information, see:
- `README.md` - Project overview
- `MIGRATION_ARCHITECTURE.md` - Technical documentation
- Discogs API docs: https://www.discogs.com/developers

