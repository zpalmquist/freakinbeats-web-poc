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

1. **Make sure you have a Discogs CSV file** (run `discogs_seller_export.py` first)

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   python3 run.py
   ```

4. **Open your browser**:
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
app/
├── routes/
│   ├── api.py           # API endpoints
│   └── main.py          # Page routes
├── services/
│   └── inventory_service.py # CSV operations
├── static/
│   ├── scss/            # SCSS stylesheets
│   └── js/              # JavaScript modules
└── templates/           # Jinja2 templates
```

## 🗄️ Database Migration (Optional)

To migrate from CSV to SQLite database:

```bash
python3 migrate_csv_to_db.py
```

Set your Discogs API token:
```bash
export DISCOGS_TOKEN="your_token_here"
```

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

- `MIGRATION_GUIDE.md` - Flask migration details
- `SCSS_GUIDE.md` - Styling guide
- `ADMIN_SETUP.md` - Admin panel setup

## 🌐 Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅
