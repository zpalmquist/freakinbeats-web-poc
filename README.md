# 🎵 Freakinbeats Web

A modular Flask ecommerce application for displaying and managing Discogs vinyl listings.

## ✨ Features

- 🖼️ **Visual Collage**: Responsive grid of vinyl record images
- 🎨 **Modern Design**: SCSS-based styling with glassmorphism effects
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🛒 **Shopping Cart**: Add items and manage cart
- 🗄️ **Database Ready**: SQLAlchemy ORM with Discogs API integration
- 🔧 **Modular**: Flask blueprints for scalable architecture

## 🚀 Quick Start

### Prerequisites

Get your Discogs API token from: https://www.discogs.com/settings/developers

### Setup Steps

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export DISCOGS_TOKEN="your_discogs_api_token"
   export DISCOGS_SELLER_USERNAME="your_seller_username"
   ```

3. **Start the server**:
   ```bash
   python3 run.py
   ```
   
   Or use the quick start script:
   ```bash
   ./start_server.sh
   ```

4. **Open your browser**:
   ```
   http://localhost:3000
   ```

The application will automatically sync with Discogs API on startup and then hourly.

## 📁 Project Structure

```
app/
├── models/
│   └── listing.py       # SQLAlchemy models
├── routes/
│   ├── api.py           # API endpoints
│   └── main.py          # Page routes
├── services/
│   ├── inventory_service.py    # Database queries
│   └── discogs_sync_service.py # API sync
├── static/
│   ├── scss/            # SCSS stylesheets
│   └── js/              # JavaScript modules
└── templates/           # Jinja2 templates

config.py              # App configuration
run.py                 # Flask application entry point
requirements.txt       # Python dependencies
start_server.sh        # Quick start script
migrate_csv_to_db.py   # Optional: Import legacy CSV data
```

## 🗄️ Database & API Integration

This application uses **SQLAlchemy ORM** with automatic **Discogs API synchronization**:

- 📊 **SQLite Database**: All listings stored locally
- 🔄 **Hourly Sync**: Automatic updates from Discogs API
- 🔍 **Advanced Search**: Query by artist, genre, format
- 📈 **Statistics**: Track inventory metrics

### Configuration

Required environment variables:
```bash
export DISCOGS_TOKEN="your_discogs_api_token"
export DISCOGS_SELLER_USERNAME="your_seller_username"
```

Optional settings in `config.py`:
- `SYNC_INTERVAL_HOURS`: Sync frequency (default: 1 hour)
- `ENABLE_AUTO_SYNC`: Enable/disable auto-sync (default: true)

### API Endpoints

- `GET /api/data` - Get all listings
- `GET /api/data/<listing_id>` - Get specific listing
- `GET /api/search?q=query&artist=name&genre=rock` - Search listings
- `GET /api/stats` - Get inventory statistics

See `MIGRATION_ARCHITECTURE.md` for detailed documentation.

## 🎨 Styling

Styles use SCSS with variables and mixins:
- Edit `app/static/scss/_variables.scss` for colors/spacing
- SCSS auto-compiles to CSS via Flask-Assets

## 🔧 Development

**Restart server**:
```bash
pkill -f "python.*server.py"
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
python3 run.py
```

**Add new routes**: Create blueprints in `app/routes/`

**Add new models**: Define in `app/models/`

## 📚 Documentation

- `QUICKSTART.md` - 5-minute setup guide
- `MIGRATION_ARCHITECTURE.md` - Technical architecture details
- `MIGRATION_SUMMARY.md` - Complete changelog

## 🌐 Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅
