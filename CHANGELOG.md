# Changelog

All notable changes to the Freakinbeats Web project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Admin Authentication System ([PR #15](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/15))

**Added:**
- ✅ Secure admin login page with passphrase authentication
- ✅ Session-based authentication with automatic timeout (1 hour)
- ✅ Rate limiting protection (5 failed attempts = 15-minute lockout)
- ✅ Constant-time passphrase comparison to prevent timing attacks
- ✅ Secure session cookies (HTTP-only, SameSite protection)
- ✅ Admin panel access control for all admin routes and API endpoints
- ✅ Beautiful, responsive login page with modern design
- ✅ Logout functionality with proper session cleanup
- ✅ Environment-based passphrase configuration
- ✅ Comprehensive documentation in `docs/ADMIN_AUTHENTICATION.md`

**Technical Details:**
- Passphrase-only authentication (no username required)
- All admin routes now require authentication (`/admin`, `/admin/*`)
- Secure session management with Flask sessions
- Brute force protection with exponential backoff
- Production-ready security configuration
- Flash messages for user feedback
- Automatic redirect to login page for unauthenticated users

**Configuration:**
```bash
# Required for admin access
ADMIN_PASSPHRASE=your_secure_admin_passphrase_here
SECRET_KEY=your_very_secure_secret_key_here
```

**Security Features:**
- Environment variable storage for passphrase
- Session-based authentication with secure cookies
- Rate limiting to prevent brute force attacks
- Timing attack prevention with constant-time comparison
- Automatic session expiry and cleanup

### Search & Filtering System ([PR #14](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/14))

**Added:**
- ✅ Comprehensive search and filtering UI on main listings page
- ✅ Freetext search across titles, artists, and labels
- ✅ Multi-faceted filtering by artist, label, year, condition, and sleeve condition
- ✅ Filter facets with aggregate counts showing available options
- ✅ Collapsible filter categories with search boxes
- ✅ Active filters display with removable tags
- ✅ Results summary showing filtered vs. total count
- ✅ Multiple simultaneous filters support
- ✅ Debounced search input (300ms delay)
- ✅ Fully responsive design matching site aesthetic

**API Endpoints:**
- `GET /api/filter` - Advanced filtering with multiple criteria
- `GET /api/facets` - Get all unique filter values with counts

**Backend Methods:**
- `InventoryService.get_filter_facets()` - Aggregate filterable fields with counts
- `InventoryService.filter_items()` - Multi-criteria filtering logic

**Frontend Components:**
- Enhanced `collage.js` with filter state management
- New `_filters.scss` with glassmorphism styling
- Updated `index.html` with complete filter UI

**Technical Details:**
- Server-side filtering for performance with large datasets
- SQLAlchemy aggregations for efficient facet counting
- Filter buttons show count of available items
- Search within filters for large lists (artists, labels)
- Maintains correct detail page linking when filtered
- Smooth animations and visual feedback

### AI-Powered Label Info Section ([PR #13](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/13))

**Added:**
- ✅ AI-generated label overviews using Google Gemini API
- ✅ Label Info section on product detail pages
- ✅ Reference links for each label (Discogs, Bandcamp, Google Search)
- ✅ Multi-label support with automatic deduplication
- ✅ Database caching system for AI-generated content
- ✅ `LabelInfo` model for persistent label overview storage
- ✅ `GeminiService` for AI integration with safety filters
- ✅ Horizontal button layout (3 buttons per row, 33% width each)
- ✅ Markdown formatting support for AI responses
- ✅ Comprehensive test suite (53 new tests)
- ✅ Utility scripts for token testing and Discogs sync
- ✅ Documentation organized into `docs/` directory

**Technical Details:**
- Gemini AI generates concise 4-sentence overviews about record labels
- Intelligent caching minimizes API costs (generate once, use forever)
- Multi-label listings display interleaved: Overview → URLs for each label
- Graceful fallback when AI is unavailable or content is blocked
- Cost-effective: ~$0.0003 per unique label with free tier (1,500 requests/day)
- 77 tests passing for complete coverage of new features
- Clean project organization with `docs/` and `utils/` directories

**Configuration:**
```bash
# Required for AI overviews (optional feature)
export GEMINI_API_KEY="your_gemini_api_key"
export ENABLE_AI_OVERVIEWS=true
```

Get your free Gemini API key from: https://ai.google.dev/

### Access Logging System ([PR #12](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/12))

**Added:**
- ✅ Comprehensive access logging system with SQLite database
- ✅ Automatic HTTP request tracking (timestamp, method, path, IP, user agent)
- ✅ Response time monitoring and performance metrics
- ✅ Access log API endpoints (`/api/logs`, `/api/logs/stats`)
- ✅ Filterable logs by path, method, IP address, and status code
- ✅ Analytics and statistics (request counts, top paths, average response times)
- ✅ `AccessLog` model for persistent log storage
- ✅ Middleware-based logging with Flask hooks
- ✅ Comprehensive documentation in `docs/ACCESS_LOGGING.md`

**Technical Details:**
- Automatic logging of all HTTP requests to database
- Indexed fields for fast queries (timestamp, path, IP, status_code)
- Built-in API endpoints for log retrieval and statistics
- Performance monitoring with response time tracking
- Privacy considerations and log retention policies
- Zero configuration required - works out of the box

**Database Schema:**
- `access_logs` table with 12 fields including timestamps, HTTP details, and performance metrics
- Indexed columns for efficient querying
- Support for filtering and aggregation queries

### YouTube Player Integration ([PR #11](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/11))

**Added:**
- ✅ YouTube player embedded in product detail pages
- ✅ New routes to fetch video data from Discogs
- ✅ Enhanced `InventoryService` to extract and handle video URLs
- ✅ App-wide style refactoring for consistency
- ✅ Global button styles and color variables
- ✅ Standardized padding and spacing

**Technical Details:**
- Product detail pages now display YouTube videos when available
- Inventory service extracts video data from Discogs API responses
- Refactored ID handling from 'index id' to database ID (preparing for UUID migration)
- SCSS refactored to reduce code repetition with shared variables and components
- Improved frontend maintainability with centralized styling

### SQLAlchemy ORM Migration ([PR #10](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/10))

**Added:**
- ✅ Complete migration from CSV-based to SQLAlchemy ORM architecture
- ✅ SQLite database with automatic table creation
- ✅ `Listing` model with 30+ fields for comprehensive vinyl data
- ✅ `DiscogsSyncService` for automatic API synchronization
- ✅ APScheduler integration for hourly background sync
- ✅ Enhanced API endpoints with search and filtering capabilities
- ✅ Migration script (`migrate_csv_to_db.py`) for CSV data import
- ✅ Comprehensive configuration system with environment variables
- ✅ Performance improvements (10-100x faster than CSV parsing)

**Technical Details:**
- SQLAlchemy ORM with indexed fields for fast lookups
- Automatic Discogs API sync with rate limiting and error handling
- Smart sync: adds new, updates existing, removes deleted listings
- Background job scheduling with graceful shutdown
- Enhanced inventory service with database queries
- Backward compatibility with existing frontend code

**New Dependencies:**
- `Flask-SQLAlchemy==3.1.1` - ORM support
- `APScheduler==3.10.4` - Job scheduling
- `requests==2.31.0` - HTTP client for API

**Configuration:**
```bash
# Required environment variables
export DISCOGS_TOKEN="your_token"
export DISCOGS_SELLER_USERNAME="your_username"
export SYNC_INTERVAL_HOURS=1
export ENABLE_AUTO_SYNC=true
```

**API Endpoints:**
- `GET /api/data` - Get all listings from database
- `GET /api/data/<listing_id>` - Get specific listing
- `GET /api/search` - Advanced search with filters
- `GET /api/stats` - Inventory statistics

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

### Access Logging Implementation ([PR #8](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/8))

**Added:**
- ✅ Comprehensive access logging system with SQLite database
- ✅ Automatic HTTP request tracking (timestamp, method, path, IP, user agent)
- ✅ Response time monitoring and performance metrics
- ✅ Access log API endpoints (`/api/logs`, `/api/logs/stats`)
- ✅ Filterable logs by path, method, IP address, and status code
- ✅ Analytics and statistics (request counts, top paths, average response times)
- ✅ `AccessLog` model for persistent log storage
- ✅ Middleware-based logging with Flask hooks
- ✅ Comprehensive documentation in `docs/ACCESS_LOGGING.md`

**Technical Details:**
- Automatic logging of all HTTP requests to database
- Indexed fields for fast queries (timestamp, path, IP, status_code)
- Built-in API endpoints for log retrieval and statistics
- Performance monitoring with response time tracking
- Privacy considerations and log retention policies
- Zero configuration required - works out of the box

**Files Added:**
- `app/middleware/access_logger.py` - Logging middleware
- `app/models/access_log.py` - AccessLog model
- `docs/ACCESS_LOGGING.md` - Comprehensive documentation
- `test_api.py` - API testing utilities

### API Testing Framework ([PR #7](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/7))

**Added:**
- ✅ Comprehensive API testing framework
- ✅ `test_api.py` with 168 lines of test coverage
- ✅ Automated testing for all API endpoints
- ✅ Test utilities for API validation
- ✅ Integration testing for Discogs API functionality

**Technical Details:**
- Complete test suite for API endpoints
- Automated testing for data retrieval and validation
- Test coverage for Discogs API integration
- Foundation for continuous integration testing

### SQLAlchemy ORM Migration ([PR #6](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/6))

**Added:**
- ✅ Complete migration from CSV-based to SQLAlchemy ORM architecture
- ✅ SQLite database with automatic table creation
- ✅ `Listing` model with 30+ fields for comprehensive vinyl data
- ✅ `DiscogsSyncService` for automatic API synchronization
- ✅ APScheduler integration for hourly background sync
- ✅ Enhanced API endpoints with search and filtering capabilities
- ✅ Migration script (`migrate_csv_to_db.py`) for CSV data import
- ✅ Comprehensive configuration system with environment variables
- ✅ Performance improvements (10-100x faster than CSV parsing)

**Technical Details:**
- SQLAlchemy ORM with indexed fields for fast lookups
- Automatic Discogs API sync with rate limiting and error handling
- Smart sync: adds new, updates existing, removes deleted listings
- Background job scheduling with graceful shutdown
- Enhanced inventory service with database queries
- Backward compatibility with existing frontend code

**Documentation Added:**
- `docs/MIGRATION_ARCHITECTURE.md` - Technical architecture details
- `docs/MIGRATION_SUMMARY.md` - Complete migration documentation
- `docs/QUICKSTART.md` - 5-minute setup guide
- `docs/SETUP_COMPLETE.md` - Setup completion guide

### Discogs Export Script ([PR #5](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/5))

**Added:**
- ✅ `/ingest` directory for data management
- ✅ `discogs_seller_export.py` - Automated Discogs data export script
- ✅ Example usage script with shell commands
- ✅ Updated CSV data with improved formatting
- ✅ Enhanced `.gitattributes` for proper file handling
- ✅ Improved README with export instructions

**Technical Details:**
- Automated script to export seller listings from Discogs
- Shell script for easy execution and automation
- Improved CSV data structure and formatting
- Better file handling and version control setup
- Foundation for automated data synchronization

**Files Added:**
- `ingest/discogs_seller_export.py` - Export automation script
- `ingest/discogs_seller_export_example_usage.sh` - Usage examples
- Updated `ingest/discogs_seller_listings.csv` - Improved data format

### Application Modularization ([PR #3](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/3))

**Added:**
- ✅ Flask blueprint architecture for scalable development
- ✅ Modular SCSS styling system with variables and mixins
- ✅ Separated JavaScript modules for different pages
- ✅ Service layer for business logic separation
- ✅ Template inheritance with base template
- ✅ Cart functionality with localStorage integration
- ✅ Product detail pages with enhanced UI
- ✅ Responsive design improvements

**Technical Details:**
- Flask blueprints for routes (`app/routes/`)
- Service layer for business logic (`app/services/`)
- SCSS compilation with Flask-Assets
- Modular JavaScript architecture
- Template inheritance and component reuse
- Cart management with browser storage
- Enhanced user interface and user experience

**Files Restructured:**
- Moved from single-file to modular architecture
- Created `app/routes/`, `app/services/`, `app/static/scss/` directories
- Separated concerns into logical modules
- Added comprehensive SCSS styling system

### UI Improvements and Data Sorting ([PR #2](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/2))

**Added:**
- ✅ Updated color gradient for improved visual appeal
- ✅ Listings sorted by posted date (newest first)
- ✅ Enhanced visual hierarchy and design consistency
- ✅ Improved user experience with better data organization

**Technical Details:**
- Updated CSS gradients for modern appearance
- Server-side sorting by posted date
- Enhanced visual design consistency
- Better data presentation and organization

### Initial Project Setup ([PR #1](https://github.com/SeaBlooms/freakinbeats-web-poc/pull/1))

**Added:**
- ✅ Flask web application foundation
- ✅ Basic vinyl record listing display with responsive grid
- ✅ SCSS-based styling with glassmorphism effects
- ✅ CSV-based data source for vinyl listings
- ✅ Modular Flask blueprint architecture
- ✅ Static file serving and asset management
- ✅ Basic search functionality
- ✅ Product detail pages with individual listings
- ✅ Responsive design for desktop, tablet, and mobile

**Technical Details:**
- Flask application with blueprint-based routing
- SCSS compilation with Flask-Assets
- CSV data parsing for vinyl listings
- Responsive grid layout for record images
- Basic search and filtering capabilities
- Foundation for future ecommerce features

---

## Legend

- ✅ Added
- 🔄 Changed
- 🗑️ Deprecated
- ❌ Removed
- 🐛 Fixed
- 🔒 Security
