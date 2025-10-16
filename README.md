# 🎵 Freakinbeats Web

A modular Flask ecommerce application for displaying and managing Discogs vinyl listings.

## ✨ Features

- 🖼️ **Visual Collage**: Responsive grid of vinyl record images
- 🔍 **Advanced Search & Filtering**: Freetext search with multi-faceted filtering by artist, label, year, and condition
- 🎨 **Modern Design**: SCSS-based styling with glassmorphism effects
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🛒 **Shopping Cart**: Add items, manage quantities, and view cart totals
- 💳 **Checkout Flow**: Server-side cart validation with tax and shipping calculations
- 🗄️ **Database Ready**: SQLAlchemy ORM with Discogs API integration
- 🔧 **Modular**: Flask blueprints for scalable architecture
- 💰 **Smart Pricing**: Automatic tax calculation and free shipping over $65

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
│   ├── listing.py       # SQLAlchemy models for vinyl listings
│   ├── access_log.py    # Access logging model
│   └── label_info.py    # AI-generated label overviews cache
├── routes/
│   ├── api.py           # API endpoints for data access
│   └── main.py          # Page routes (including admin & checkout)
├── services/
│   ├── inventory_service.py    # Database queries & filtering
│   ├── discogs_sync_service.py # Discogs API synchronization
│   ├── cart_service.py         # Cart validation & calculations
│   └── gemini_service.py       # AI label overview generation
├── middleware/
│   └── access_logger.py # Request logging middleware
├── static/
│   ├── css/             # Compiled CSS files
│   │   ├── admin.css    # Admin panel styles
│   │   ├── cart.css     # Shopping cart styles
│   │   ├── checkout.css # Checkout page styles
│   │   ├── detail.css   # Product detail styles
│   │   └── main.css     # Main site styles
│   ├── scss/            # SCSS source files
│   │   ├── _base.scss   # Base styles & mixins
│   │   ├── _filters.scss # Search & filter styles
│   │   ├── _variables.scss # Global variables
│   │   ├── _vinyl.scss  # Vinyl-specific styles
│   │   ├── cart.scss    # Cart page styles
│   │   ├── checkout.scss # Checkout page styles
│   │   ├── detail.scss  # Product detail styles
│   │   └── main.scss    # Main site styles
│   └── js/              # JavaScript modules
│       ├── admin.js     # Admin panel functionality
│       ├── cart-utils.js # Shared cart utilities
│       ├── cart.js      # Cart page logic
│       ├── checkout.js  # Checkout page logic
│       ├── collage.js   # Main listings page logic
│       └── detail.js    # Product detail logic
└── templates/           # Jinja2 templates
    ├── admin_login.html # Admin authentication page
    ├── admin.html       # Admin panel page
    ├── base.html        # Base template
    ├── index.html       # Home page with listings
    ├── cart.html        # Shopping cart
    ├── checkout.html    # Checkout page
    └── detail.html      # Product details

config.py              # App configuration & environment settings
run.py                 # Flask application entry point
requirements.txt       # Python dependencies
start_server.sh        # Quick start script

docs/                  # Documentation
├── ACCESS_LOGGING.md  # Access logging implementation
├── ADMIN_AUTHENTICATION.md # Admin login system
├── AI_LABEL_OVERVIEWS.md # AI label overview feature
├── MIGRATION_ARCHITECTURE.md # Technical architecture
├── MIGRATION_SUMMARY.md # Complete changelog
├── QUICKSTART.md      # 5-minute setup guide
├── SETUP_AI_OVERVIEWS.md # Gemini AI setup
└── SETUP_COMPLETE.md  # Setup completion guide

tests/                 # Test suite
├── conftest.py        # Pytest configuration
├── fixtures/          # Test data factories
└── services/          # Service layer tests

utils/                 # Utility scripts
├── migrate_csv_to_db.py # Import legacy CSV data
├── sync_discogs.py    # Manual Discogs sync
├── test_api.py        # API testing utilities
└── test_discogs_token.py # Token validation
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

**Inventory & Data:**
- `GET /api/data` - Get all listings
- `GET /api/data/<listing_id>` - Get specific listing
- `GET /api/search?q=query&artist=name&genre=rock` - Search listings
- `GET /api/filter?q=query&artist=name&label=name&year=2020&condition=Mint&sleeve_condition=VG+` - Advanced filtering
- `GET /api/facets` - Get filter facets with counts for all filterable fields
- `GET /api/stats` - Get inventory statistics

**Shopping Cart & Checkout:**
- `POST /checkout/validate` - Validate cart items and calculate totals
- `POST /checkout/prepare-payment` - Prepare cart data for payment processing

**Access Logging:**
- `GET /api/logs` - Get access logs with optional filters
- `GET /api/logs/stats` - Get access log statistics

See `MIGRATION_ARCHITECTURE.md` for detailed documentation.

## 🔍 Search & Filtering

The main listings page includes a comprehensive search and filtering system:

### Search Features
- **Freetext Search**: Search across titles, artists, and labels
- **Debounced Input**: 300ms delay prevents excessive API calls
- **Clear Button**: Quick reset of search query
- **Real-time Results**: Instant filtering as you type

### Filter Categories

**Artist Filter:**
- Filter by primary artist name
- Search within artists list
- Shows listing count per artist
- Sorted by most listings

**Label Filter:**
- Filter by record label
- Search within labels list
- Shows listing count per label
- Sorted by most listings

**Year Filter:**
- Filter by release year
- Search within years list
- Shows listing count per year
- Sorted chronologically (newest first)

**Condition Filter:**
- Filter by media condition (Mint, Near Mint, VG+, etc.)
- Shows listing count per condition
- Quick toggle buttons

**Sleeve Condition Filter:**
- Filter by sleeve/jacket condition
- Shows listing count per condition
- Independent from media condition

### Filtering UI

**Collapsible Categories:**
- Click category headers to expand/collapse
- Only one category open at a time
- Arrow indicators show open/closed state

**Active Filters Display:**
- Visual tags show all active filters
- Remove individual filters via × button
- "Clear All" button resets everything
- Shows "Showing X of Y records" count

**Multiple Simultaneous Filters:**
- Apply filters from different categories at once
- Filters are ANDed together (all must match)
- Search query applies across filtered results

**Filter Search:**
- Search within large filter lists (artists, labels, years)
- Helps find specific values quickly
- Real-time filtering of options

### Technical Implementation

**Backend:**
```python
# Get filter facets with counts
facets = inventory_service.get_filter_facets()
# Returns: {'artists': [...], 'labels': [...], 'years': [...], etc.}

# Apply multiple filters
results = inventory_service.filter_items(
    query='techno',
    artist='Aphex Twin',
    year='1995',
    condition='Mint (M)'
)
```

**Frontend:**
- `DiscogsCollage` class manages filter state
- Parallel API calls for data and facets
- LocalStorage persistence planned
- Smooth animations and transitions

**Styling:**
- Glassmorphism design matching overall aesthetic
- Fully responsive (mobile, tablet, desktop)
- Sticky filter search bars within scrollable lists
- Active state indicators for selected filters

## 🛒 Shopping Cart & Checkout

The application includes a full-featured shopping cart and checkout system:

### Cart Features
- **LocalStorage Persistence**: Cart data persists across browser sessions
- **Real-time Updates**: Instant feedback on add/remove actions
- **Quantity Management**: Adjust quantities for each item
- **Price Calculations**: Automatic subtotal and total calculations
- **Cart Validation**: Server-side validation ensures items are still available

### Checkout Process
1. **Cart Review** (`/cart`) - View and modify items before checkout
2. **Checkout** (`/checkout`) - Validate cart and view order summary
3. **Payment** (Coming Soon) - Stripe integration planned

### CartService Features

The `CartService` handles all cart-related business logic:

```python
# Cart validation with inventory checks
is_valid, items, total, currency = cart_service.validate_cart(cart_items)

# Calculate totals with tax and shipping
summary = cart_service.calculate_cart_summary(validated_items, customer_address)

# Prepare for payment processing
payment_data = cart_service.prepare_cart_for_payment(cart_items, customer_address)
```

**Pricing Rules:**
- **Tax Calculation**: Default 8.5% rate (location-based tax support planned)
- **Shipping**: $6.50 flat rate, FREE for orders $65+
- **Currency Support**: Multi-currency display (USD default)

### Client-Side Cart Utilities

Shared cart utilities (`cart-utils.js`) provide consistent cart management:
- `getCart()` - Retrieve current cart from localStorage
- `saveCart(cart)` - Save cart to localStorage
- `addToCart(item)` - Add item with duplicate detection
- `removeFromCart(listingId)` - Remove item by ID
- `updateQuantity(listingId, quantity)` - Update item quantity
- `clearCart()` - Empty the cart
- `formatPrice(amount, currency)` - Format price display

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

All documentation has been organized in the `docs/` directory:
- `docs/QUICKSTART.md` - 5-minute setup guide
- `docs/MIGRATION_ARCHITECTURE.md` - Technical architecture details
- `docs/MIGRATION_SUMMARY.md` - Complete changelog
- `docs/ACCESS_LOGGING.md` - Access logging implementation details
- `docs/AI_LABEL_OVERVIEWS.md` - AI label overview feature documentation
- `docs/SETUP_AI_OVERVIEWS.md` - Quick setup guide for Gemini AI

Utility scripts are in the `utils/` directory:
- `utils/migrate_csv_to_db.py` - Import listings from CSV files
- `utils/sync_discogs.py` - Manually sync with Discogs API
- `utils/test_discogs_token.py` - Test Discogs API token validity


## 🌐 Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅
