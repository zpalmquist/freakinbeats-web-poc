# 🎵 Freakinbeats Web

A modular Flask ecommerce application for displaying and managing Discogs vinyl listings.

## ✨ Features

- 🖼️ **Visual Collage**: Responsive grid of vinyl record images
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
│   ├── listing.py       # SQLAlchemy models
│   └── access_log.py    # Access logging model
├── routes/
│   ├── api.py           # API endpoints
│   └── main.py          # Page routes (including checkout)
├── services/
│   ├── inventory_service.py    # Database queries
│   ├── discogs_sync_service.py # API sync
│   └── cart_service.py         # Cart validation & calculations
├── static/
│   ├── scss/            # SCSS stylesheets
│   │   ├── checkout.scss      # Checkout page styles
│   │   └── _variables.scss    # Global variables
│   └── js/              # JavaScript modules
│       ├── cart-utils.js      # Shared cart utilities
│       ├── cart.js            # Cart page logic
│       ├── checkout.js        # Checkout page logic
│       └── detail.js          # Product detail logic
└── templates/           # Jinja2 templates
    ├── index.html       # Home page
    ├── cart.html        # Shopping cart
    ├── checkout.html    # Checkout page
    └── detail.html      # Product details

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

**Inventory & Data:**
- `GET /api/data` - Get all listings
- `GET /api/data/<listing_id>` - Get specific listing
- `GET /api/search?q=query&artist=name&genre=rock` - Search listings
- `GET /api/stats` - Get inventory statistics

**Shopping Cart & Checkout:**
- `POST /checkout/validate` - Validate cart items and calculate totals
- `POST /checkout/prepare-payment` - Prepare cart data for payment processing

**Access Logging:**
- `GET /api/logs` - Get access logs with optional filters
- `GET /api/logs/stats` - Get access log statistics

See `MIGRATION_ARCHITECTURE.md` for detailed documentation.

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

- `QUICKSTART.md` - 5-minute setup guide
- `MIGRATION_ARCHITECTURE.md` - Technical architecture details
- `MIGRATION_SUMMARY.md` - Complete changelog
- `ACCESS_LOGGING.md` - Access logging implementation details

## 📦 Recent Changes

### Checkout Routes Feature ([PR #9](https://github.com/SeaBlooms/freakinbeats-web-poc/commit/59e0d9cb9e5c080d5e2bb5b67a0abfb302433a85))

**Added:**
- ✅ Full checkout flow with cart validation
- ✅ `CartService` for business logic (validation, tax, shipping)
- ✅ Checkout page (`/checkout`) with order summary
- ✅ Cart utilities module for consistent cart management
- ✅ Server-side validation endpoints
- ✅ Tax and shipping calculation
- ✅ Free shipping for orders $65+
- ✅ Checkout-specific styling and responsive design

**Technical Details:**
- Server-side cart validation prevents checkout with unavailable items
- Cart data stored in browser localStorage
- Real-time price calculations with currency formatting
- Modular JavaScript architecture with shared utilities
- SCSS styling with glassmorphism effects

## 🌐 Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅
