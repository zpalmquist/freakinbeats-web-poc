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
- 🔐 **Admin Panel**: Secure passphrase-authenticated dashboard with access logs, Discogs sync control, and AI cache management
- 🤖 **AI Label Overviews**: Google Gemini-powered record label descriptions with history and musical context
- 📊 **Access Logging**: Comprehensive request tracking with statistics, filtering, and export capabilities

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
   # Required: Discogs API integration
   export DISCOGS_TOKEN="your_discogs_api_token"
   export DISCOGS_SELLER_USERNAME="your_seller_username"
   
   # Required: Admin panel access
   export ADMIN_PASSPHRASE="your_secure_passphrase"
   export SECRET_KEY="your_secret_key_for_sessions"
   
   # Optional: AI label overviews (defaults to enabled if key present)
   export GEMINI_API_KEY="your_google_gemini_api_key"
   export ENABLE_AI_OVERVIEWS="true"
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
│   │   ├── _base.scss   # Base styles & reset
│   │   ├── _components.scss # 42 reusable UI component mixins
│   │   ├── _filters.scss # Search & filter styles
│   │   ├── _icons.scss  # Lucide Icons integration
│   │   ├── _icons-admin.scss # Admin-specific icon styles
│   │   ├── _variables.scss # Global variables & design tokens
│   │   ├── _vinyl.scss  # Vinyl-specific styles
│   │   ├── admin.scss   # Admin panel page styles
│   │   ├── cart.scss    # Cart page styles
│   │   ├── checkout.scss # Checkout page styles
│   │   ├── detail.scss  # Product detail styles
│   │   └── main.scss    # Main site styles (imports partials)
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

**Required environment variables:**
```bash
# Discogs API Integration
export DISCOGS_TOKEN="your_discogs_api_token"
export DISCOGS_SELLER_USERNAME="your_seller_username"

# Admin Panel Access
export ADMIN_PASSPHRASE="your_secure_passphrase"
export SECRET_KEY="your_secret_key_for_sessions"
```

**Optional environment variables:**
```bash
# AI Label Overviews (Google Gemini)
export GEMINI_API_KEY="your_google_gemini_api_key"
export ENABLE_AI_OVERVIEWS="true"  # default: true

# Discogs Sync Control
export ENABLE_AUTO_SYNC="true"  # default: true
```

**Optional settings in `config.py`:**
- `SYNC_INTERVAL_HOURS`: Sync frequency (default: 1 hour)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `PORT`: Server port (default: 3000)

### API Endpoints

**Page Routes:**
- `GET /` - Main listings page with collage view
- `GET /cart` - Shopping cart page
- `GET /detail/<listing_id>` - Product detail page
- `GET /checkout` - Checkout page

**Inventory & Data:**
- `GET /api/data` - Get all listings
- `GET /api/data/<int:id>` - Get specific listing by database ID
- `GET /api/data/<listing_id>` - Get specific listing by Discogs listing ID
- `GET /api/detail/<int:id>` - Get listing with videos by database ID
- `GET /api/detail/<listing_id>` - Get listing with videos by Discogs listing ID
- `GET /api/search?q=query&artist=name&genre=rock&format=Vinyl` - Search listings with filters
- `GET /api/filter?q=query&artist=name&label=name&year=2020&condition=Mint&sleeve_condition=VG+` - Advanced multi-criteria filtering
- `GET /api/facets` - Get filter facets with counts for all filterable fields (artists, labels, years, conditions)
- `GET /api/stats` - Get inventory statistics (total count, by condition, by format, etc.)

**Shopping Cart & Checkout:**
- `POST /checkout/validate` - Validate cart items, check availability, calculate totals with tax and shipping
- `POST /checkout/prepare-payment` - Prepare cart data for Stripe payment processing

**Access Logging:**
- `GET /api/logs?limit=100&path=/api/data&method=GET&ip=127.0.0.1` - Get access logs with optional filters
- `GET /api/logs/stats` - Get access log statistics (requests by method, status code, top paths, avg response time)

**Admin Panel (Requires Authentication):**
- `GET /admin-login` - Admin login page
- `POST /admin-login` - Process admin authentication (passphrase verification with rate limiting)
- `POST /admin-logout` - Logout admin session
- `GET /admin` - Admin dashboard page (requires auth)
- `GET /admin/access-logs?page=1&per_page=50&search=&method=GET&status=200` - Paginated access logs with search and filtering
- `POST /admin/sync-discogs` - Trigger manual Discogs synchronization (returns sync stats)
- `POST /admin/clear-label-cache` - Clear all cached AI label overviews
- `POST /admin/regenerate-label-overview` - Regenerate specific label overview (body: `{"label_name": "Label Name"}`)

See `MIGRATION_ARCHITECTURE.md` for detailed documentation.

##  Search & Filtering

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

**Backend Services (app/services/):**

`inventory_service.py` - Core inventory and filtering logic
```python
class InventoryService:
    def get_all_items() -> list[dict]
        # Returns all listings with basic info
        
    def get_item_by_id(id: int) -> dict
        # Fetch by database primary key
        
    def get_item_by_listing_id(listing_id: str) -> dict
        # Fetch by Discogs listing ID
        
    def get_item_with_videos(listing_id: str) -> dict
        # Includes YouTube video URLs from Discogs
        
    def search_items(query, artist, genre, format_type) -> list[dict]
        # Freetext search with optional filters
        
    def filter_items(query, artist, label, year, condition, sleeve_condition) -> list[dict]
        # Multi-criteria filtering with ANDed conditions
        # Uses SQLAlchemy ORM with LIKE queries
        
    def get_filter_facets() -> dict
        # Returns available filter values with counts
        # Example: {'artists': [{'value': 'Aphex Twin', 'count': 12}], ...}
        
    def get_stats() -> dict
        # Inventory statistics: total, by condition, by format
```

`discogs_sync_service.py` - Discogs API integration
```python
class DiscogsSyncService:
    def sync_all_listings() -> dict
        # Fetches inventory from Discogs API
        # Updates local database (add/update/remove)
        # Returns stats: {'added': 5, 'updated': 10, 'removed': 2}
        
    # Uses discogs_client library
    # Respects rate limits (60 requests/min)
    # Handles pagination automatically
```

**Frontend Architecture (app/static/js/):**

`collage.js (401 lines)` - Main listings controller
```javascript
class DiscogsCollage {
    constructor() {
        this.filters = { query: '', artist: '', label: '', year: '', condition: '', sleeve_condition: '' }
        this.allData = []
        this.filteredData = []
    }
    
    async init()
        // Parallel API calls: fetchData() + fetchFacets()
        // Renders initial collage grid
        
    async fetchData()
        // GET /api/data - Fetch all listings
        
    async fetchFacets()
        // GET /api/facets - Get filter options with counts
        
    applyFilters()
        // Client-side filtering with debounce (300ms)
        // API call: GET /api/filter with query params
        
    renderCollage()
        // Generates vinyl card grid
        // Lazy loading images
        // Click handlers for detail navigation
        
    updateActiveFilters()
        // Shows active filter tags
        // "Clear All" functionality
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    new DiscogsCollage();
});
```

**Database Schema (SQLAlchemy ORM):**

```python
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String, unique=True)  # Discogs ID
    release_id = db.Column(db.Integer)
    release_title = db.Column(db.String)
    artist_names = db.Column(db.String)  # Comma-separated
    label = db.Column(db.String)
    year = db.Column(db.Integer)
    condition = db.Column(db.String)  # Media condition
    sleeve_condition = db.Column(db.String)
    price_value = db.Column(db.Float)
    price_currency = db.Column(db.String)
    thumb_url = db.Column(db.String)  # Thumbnail image
    # ... additional fields
```

**API Flow:**
```
User Action → JavaScript Event → API Request → Service Layer → Database Query → JSON Response → DOM Update

Example:
1. User types "techno" in search box
2. debounced input handler (300ms) triggers
3. collage.applyFilters() called
4. GET /api/filter?q=techno
5. inventory_service.filter_items(query='techno')
6. SQLAlchemy query: Listing.query.filter(Listing.release_title.ilike('%techno%'))
7. JSON response with filtered listings
8. collage.renderCollage() updates DOM
```

**Performance Optimizations:**
- **Debounced search**: 300ms delay prevents API spam
- **Parallel requests**: Data and facets fetched simultaneously
- **Client-side caching**: All data loaded once, filtered locally when possible
- **Lazy image loading**: `loading="lazy"` attribute on images
- **Database indexes**: On listing_id, artist_names, label, year
- **Query optimization**: Uses select_from() and joins efficiently

**State Management:**
```javascript
// Filter state stored in DiscogsCollage instance
this.filters = {
    query: '',           // Freetext search
    artist: '',          // Selected artist
    label: '',           // Selected label
    year: '',            // Selected year
    condition: '',       // Media condition
    sleeve_condition: '' // Sleeve condition
}

// State updates trigger:
// 1. applyFilters() - Fetch filtered data
// 2. updateActiveFilters() - Update UI tags
// 3. renderCollage() - Re-render grid
```

**Styling:**
- Glassmorphism design matching overall aesthetic
- Fully responsive (mobile, tablet, desktop)
- Sticky filter search bars within scrollable lists
- Active state indicators for selected filters
- Smooth transitions (CSS: `transition: all 0.3s ease`)

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

Shared cart utilities (`cart-utils.js`, 150 lines) provide consistent cart management:
- `getCart()` - Retrieve current cart from localStorage
- `saveCart(cart)` - Save cart to localStorage
- `addToCart(item)` - Add item with duplicate detection
- `removeFromCart(listingId)` - Remove item by ID
- `updateQuantity(listingId, quantity)` - Update item quantity
- `clearCart()` - Empty the cart
- `formatPrice(amount, currency)` - Format price display

### Technical Implementation

**Backend Service (cart_service.py):**

```python
class CartService:
    def validate_cart(cart_items: list[dict]) -> tuple[bool, list, float, str]
        # Validates each item exists in inventory
        # Checks current availability and pricing
        # Returns: (is_valid, validated_items, total_price, currency)
        
    def calculate_cart_summary(validated_items: list[dict], customer_address: dict = None) -> dict
        # Calculates subtotal, tax, shipping, total
        # Applies free shipping rules (orders $65+)
        # Returns: {
        #   'subtotal': 45.00,
        #   'tax': 3.83,          # 8.5% default
        #   'shipping': 6.50,     # FREE if subtotal >= $65
        #   'total': 55.33,
        #   'currency': 'USD'
        # }
        
    def prepare_cart_for_payment(cart_items: list[dict], customer_address: dict) -> dict
        # Formats data for Stripe API
        # Includes line items, amounts, customer info
        # Returns Stripe-compatible payload
        
    def get_cart_for_stripe(cart_items: list[dict]) -> dict
        # Alternate method for Stripe preparation
        # Similar to prepare_cart_for_payment
```

**Pricing Rules:**
```python
TAX_RATE = 0.085              # 8.5% default (location-based planned)
SHIPPING_COST = 6.50          # Flat rate shipping
FREE_SHIPPING_THRESHOLD = 65  # Free shipping on orders $65+

# Tax calculation
tax = subtotal * TAX_RATE

# Shipping calculation  
shipping = SHIPPING_COST if subtotal < FREE_SHIPPING_THRESHOLD else 0.00

# Total
total = subtotal + tax + shipping
```

**Frontend Cart Management:**

`cart-utils.js (150 lines)` - Shared utilities
```javascript
class CartUtils {
    static getCart() {
        // Retrieve from localStorage
        // Returns: [{listing_id, title, price, quantity, ...}]
    }
    
    static saveCart(cart) {
        // Persist to localStorage
        // Key: 'vinyl_cart'
    }
    
    static addToCart(item) {
        // Duplicate detection: check if item already in cart
        // If exists: increment quantity
        // If new: add with quantity = 1
        // Auto-save after modification
    }
    
    static removeFromCart(listingId) {
        // Filter out item by listing_id
        // Auto-save after modification
    }
    
    static updateQuantity(listingId, quantity) {
        // Update specific item quantity
        // Validate: quantity must be >= 1
        // Auto-save after modification
    }
    
    static clearCart() {
        // Empty cart and save
    }
    
    static formatPrice(amount, currency = 'USD') {
        // Format: $45.00
        // Uses Intl.NumberFormat for locale support
    }
    
    static getCartCount() {
        // Returns total number of items (sum of quantities)
    }
    
    static getCartTotal() {
        // Calculate sum of (price * quantity) for all items
    }
}
```

`cart.js (107 lines)` - Cart page controller
```javascript
// Cart page functionality
- Render cart items in table/list
- Quantity adjustment controls
- Remove item buttons
- Subtotal and total display
- "Proceed to Checkout" button
- Empty cart state UI
```

`checkout.js (119 lines)` - Checkout page controller
```javascript
class CheckoutPage {
    async init() {
        // Fetch cart from localStorage
        // Call POST /checkout/validate
        // Display order summary with tax and shipping
    }
    
    async validateCart() {
        // POST /checkout/validate with cart items
        // Server responds with validated items and totals
        // Shows any out-of-stock or price-changed items
    }
    
    async preparePayment() {
        // POST /checkout/prepare-payment
        // Get Stripe-formatted data
        // Ready for payment processing
    }
}
```

**LocalStorage Schema:**
```javascript
// Key: 'vinyl_cart'
// Value: JSON array
[
    {
        listing_id: "123456789",
        title: "Aphex Twin - Selected Ambient Works 85-92",
        artist: "Aphex Twin",
        price: 25.00,
        currency: "USD",
        quantity: 1,
        thumb_url: "https://...",
        condition: "Near Mint (NM or M-)",
        sleeve_condition: "Very Good Plus (VG+)"
    },
    // ... more items
]
```

**Checkout Flow:**
```
1. User clicks "Add to Cart" on detail page
   └─> CartUtils.addToCart(item) → localStorage updated

2. Cart badge updates with count
   └─> CartUtils.getCartCount() → Display in header

3. User navigates to /cart
   └─> cart.js loads and renders items
   └─> Shows subtotal (no tax/shipping yet)

4. User clicks "Proceed to Checkout"
   └─> Navigate to /checkout

5. Checkout page validates cart
   └─> POST /checkout/validate
   └─> Server checks inventory, calculates tax/shipping
   └─> Display full order summary

6. User enters payment details (planned)
   └─> POST /checkout/prepare-payment
   └─> Stripe integration (coming soon)
```

**Error Handling:**
```javascript
// Out of stock
if (!item.available) {
    showError('Item is no longer available');
    removeFromCart(item.listing_id);
}

// Price changed
if (item.current_price !== item.cart_price) {
    showWarning('Price has changed');
    updateCartPrice(item.listing_id, item.current_price);
}

// Validation failures
if (!validation.is_valid) {
    showErrors(validation.errors);
    // User must fix issues before proceeding
}
```

## 🔐 Admin Panel

The application includes a secure, feature-rich admin panel for managing inventory and monitoring site activity.

### Features

**Access Log Monitoring:**
- View all HTTP requests with detailed information
- Search across paths, IP addresses, and user agents
- Filter by HTTP method (GET, POST, etc.) and status code
- Pagination with configurable page size (default: 50 records)
- Real-time refresh capability
- Modal detail view for comprehensive log inspection
- Export logs to CSV (client-side)

**Discogs Synchronization:**
- Manual trigger for Discogs API sync
- Real-time sync status and progress feedback
- View sync statistics (added, updated, removed records)

**AI Cache Management:**
- Clear all cached AI-generated label overviews
- Regenerate individual label descriptions
- View cache statistics

### Access

Navigate to `/admin-login` in your browser and authenticate with your passphrase.

### Configuration

**Required environment variables:**
```bash
# Admin authentication passphrase (no username needed)
export ADMIN_PASSPHRASE="your_secure_passphrase"

# Session encryption key (generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
export SECRET_KEY="your_secret_key_for_sessions"
```

**Optional in `config.py`:**
- Session timeout and security settings
- Rate limiting thresholds

### Security Features

- **Passphrase-only authentication**: No username required, single passphrase entry
- **Rate limiting**: 5 failed login attempts trigger a 15-minute lockout
- **Constant-time comparison**: Prevents timing attacks on passphrase verification
- **Session-based authorization**: All admin endpoints require valid session
- **Permanent sessions**: Stay logged in across browser restarts
- **CSRF protection**: Form validation for state-changing operations

### Admin API Endpoints

**Authentication:**
- `GET /admin-login` - Admin login page
- `POST /admin-login` - Process admin authentication
- `POST /admin-logout` - Logout and clear session

**Dashboard & Logs:**
- `GET /admin` - Admin dashboard (requires authentication)
- `GET /admin/access-logs?page=1&per_page=50&search=&method=&status=` - Paginated access logs with filtering

**Inventory Management:**
- `POST /admin/sync-discogs` - Trigger manual Discogs synchronization
- `POST /admin/clear-label-cache` - Clear all cached AI label overviews
- `POST /admin/regenerate-label-overview` - Regenerate specific label overview (body: `{"label_name": "..."}`)

### Technical Details

**Frontend (admin.js):**
- 743 lines of JavaScript
- `AdminPanel` class handles all interactions
- Debounced search (500ms)
- Keyboard shortcuts (ESC to close modal, Ctrl/Cmd+R to refresh)
- Dynamic filter application
- Modal management for log details

**Styling:**
- Dedicated `admin.scss` and compiled `admin.css`
- Consistent with main site design
- Responsive table layout
- Glassmorphism effects matching site aesthetic

**Rate Limiting Implementation:**
```python
# 5 failed attempts
# 15-minute lockout window
# Automatic reset after timeout
```

See `docs/ADMIN_AUTHENTICATION.md` for complete documentation.

## 🎨 Styling

The application uses a comprehensive SCSS-based styling system with modern design patterns and reusable components.

### Quick Reference

**Edit styles:** Modify SCSS files in `app/static/scss/`  
**Compile CSS:** Run `python3 compile_assets.py`  
**Auto-compile:** Flask-Assets compiles SCSS automatically in development mode  
**Production:** Pre-compile with `compile_assets.py` before deployment  

### Architecture Overview

```
SCSS Source Files (3,621 lines)          →  Compiled CSS (5 files, ~86KB total)
├── Partials (imported by page files)   →  
│   ├── _variables.scss (280 lines)     →  [Design tokens & color system]
│   ├── _components.scss (775 lines)    →  [42 reusable UI mixins]
│   ├── _base.scss (97 lines)           →  [CSS reset & base styles]
│   ├── _icons.scss (132 lines)         →  [Lucide Icons system]
│   ├── _icons-admin.scss (90 lines)    →  [Admin icon styles]
│   ├── _filters.scss (346 lines)       →  [Search & filter UI]
│   └── _vinyl.scss (24 lines)          →  [Vinyl record card styles]
│
└── Page Files (compile to CSS)          →  Output
    ├── main.scss (99 lines)             →  main.css (24KB)
    ├── detail.scss (421 lines)          →  detail.css (15KB)
    ├── cart.scss (128 lines)            →  cart.css (7KB)
    ├── checkout.scss (232 lines)        →  checkout.css (8.6KB)
    └── admin.scss (997 lines)           →  admin.css (31KB)
```

### Design System

**_variables.scss (280 lines)** - Design tokens and theme configuration
```scss
// Color System
$gradient-start, $gradient-end          // Background gradients
$admin-primary, $admin-secondary        // Admin theme colors
$status-success, $status-warning, etc.  // Status indicators
$neutral-100 through $neutral-900       // Grayscale palette

// Spacing Scale (rem-based)
$spacing-xs: 0.25rem  →  $spacing-xxl: 4rem

// Typography
$font-stack: system font stack with fallbacks
$font-mono: monospace for code/data
$line-height-base: 1.5

// Transparency Utilities
$white-alpha-10 through $white-alpha-90
$black-alpha-10 through $black-alpha-90

// Mixins
@mixin vinyl-info-text    // Monochromatic text styling
@mixin glassmorphism      // Frosted glass effect
```

**_components.scss (775 lines)** - 42 reusable UI component mixins
```scss
// Button System
@mixin btn-base, @mixin btn-primary, @mixin btn-secondary
@mixin btn-glass  // Glassmorphism buttons

// Card System  
@mixin card-base, @mixin card-glass
@mixin card-hover  // Interactive card states

// Layout
@mixin flex-center, @mixin flex-between
@mixin grid-auto-fit($min-width)  // Responsive grids

// Form Elements
@mixin input-base, @mixin input-glass
@mixin select-base, @mixin checkbox-custom

// Modal System
@mixin modal-base, @mixin modal-backdrop
@mixin modal-content  // Content area styling

// Table System
@mixin table-base, @mixin table-striped
@mixin table-responsive  // Mobile-friendly tables

// Badge & Status
@mixin badge-base, @mixin badge-status($color)
@mixin status-indicator  // Colored status dots

// Animations
@mixin fade-in($duration), @mixin slide-up($duration)
@mixin pulse-animation  // Attention-grabbing effect
```

**_icons.scss (132 lines)** - Lucide Icons integration
```scss
// Icon System - CDN-based, ~1KB per icon, 850+ available
// Sizing: Uses `em` units (relative to font-size)
// Alignment: display: inline-flex + align-items: center

.icon { width: 1em; height: 1em; }  // Scales with text
.btn .icon { margin-right: 0.5rem; }  // Button icons
```

**_filters.scss (346 lines)** - Search and filtering UI
```scss
// Filter Panel
.filter-panel       // Container with glassmorphism
.filter-section     // Collapsible category sections
.filter-btn         // Individual filter buttons with counts

// Active Filters
.active-filters     // Tag display area
.filter-tag         // Individual removable tags

// Search Integration
.filter-search      // Search within filter options
```

### JavaScript Modules (1,890 lines total)

**Client-Side Architecture:**
```javascript
// Core Classes
DiscogsCollage (401 lines)   // Main listings page, filtering, API calls
AdminPanel (742 lines)        // Admin dashboard, logs viewer, sync control
CheckoutPage (119 lines)      // Checkout validation, payment prep
CartUtils (150 lines)         // Shared cart management utilities

// Page Controllers
cart.js (107 lines)           // Cart page logic
detail.js (371 lines)         // Product detail page, image viewer
```

### Icon System (Lucide Icons)

**Integration:** CDN-based (unpkg.com)  
**Library Size:** ~1KB per icon, 850+ icons available  
**Usage Pattern:**
```html
<!-- Icons scale with font-size, flexbox ensures alignment -->
<button>
  <i data-lucide="shopping-cart"></i>
  Add to Cart
</button>
```

**Key Features:**
- Em-based sizing (icons scale with text)
- Flexbox alignment (vertically centered)
- Gap spacing (0.5rem between icon and text)
- Consistent stroke width across all icons

### Page-Specific Styles

**main.scss (99 lines) → main.css (24KB)**
- Imports all partials
- Vinyl collage grid layout
- Filter panel positioning
- Responsive breakpoints

**detail.scss (421 lines) → detail.css (15KB)**  
- Product detail layout
- Image gallery/lightbox
- Specifications table
- Add to cart section

**cart.scss (128 lines) → cart.css (7KB)**
- Cart item list
- Quantity controls
- Price summary
- Empty cart state

**checkout.scss (232 lines) → checkout.css (8.6KB)**
- Multi-step layout
- Payment form styling
- Order summary
- Validation states

**admin.scss (997 lines) → admin.css (31KB)**
- Dashboard layout
- Access log table
- Filter controls
- Modal overlays
- Sync status indicators

### Responsive Design

**Breakpoints:**
```scss
$mobile: 576px
$tablet: 768px
$desktop: 992px
$large: 1200px
```

**Mobile-First Approach:**
- Base styles target mobile
- Media queries add complexity for larger screens
- Grid layouts use `auto-fit` for responsiveness
- Tables transform to cards on mobile

### Glassmorphism Theme

**Visual Identity:**
- Frosted glass backgrounds (`backdrop-filter: blur()`)
- Semi-transparent layers with subtle borders
- Gradient overlays for depth
- Smooth transitions and hover states

### Development Workflow

1. **Edit SCSS files** in `app/static/scss/`
2. **Auto-compile** happens on page reload (development)
3. **Manual compile** with `python3 compile_assets.py`
4. **Production build** runs compile_assets before deployment

### For LLM/AI Assistants

**When modifying styles:**
- Edit SCSS files, not compiled CSS
- Use existing mixins from `_components.scss`
- Follow design tokens from `_variables.scss`
- Test responsive layouts at all breakpoints
- Run compile_assets.py to generate CSS

**Common tasks:**
```bash
# Compile all SCSS to CSS
python3 compile_assets.py

# Check SCSS syntax
sass --check app/static/scss/*.scss

# Find specific styles
grep -r "mixin\|class" app/static/scss/
```

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
