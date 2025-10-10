# freakinbeats-web-poc
freakinbeats.com

# 🎵 Discogs Vinyl Collection Collage

A beautiful web application that displays all your Discogs vinyl listings as an interactive image collage.

## ✨ Features

- 🖼️ **Visual Collage**: All vinyl record images displayed in a responsive grid
- 📊 **Statistics**: Collection stats including total items, average price, and total value
- 🎨 **Modern Design**: Beautiful gradient background with glassmorphism effects
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices
- 🔍 **Interactive**: Click on any vinyl to see detailed information
- ⚡ **Fast Loading**: Lazy loading images for better performance

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Make sure you have a Discogs CSV file** (run the export script in `ingest/` first):
   ```bash
   cd ingest
   python3 discogs_seller_export.py --seller YOUR_SELLER_NAME
   cd ..
   ```

3. **Start the server**:
   ```bash
   ./start_server.sh
   ```
   
   Or manually:
   ```bash
   python3 run.py
   ```

4. **Open your browser** and visit:
   ```
   http://localhost:3000
   ```

## 📁 File Structure

```
freakinbeats-web-poc/
├── app/
│   ├── __init__.py                     # Flask app factory
│   ├── routes/
│   │   ├── main.py                     # Main page routes
│   │   └── api.py                      # API endpoints
│   ├── services/
│   │   └── inventory_service.py        # Business logic for inventory
│   ├── static/
│   │   ├── css/                        # Compiled CSS
│   │   ├── js/                         # JavaScript files
│   │   └── scss/                       # SCSS source files
│   └── templates/
│       ├── base.html                   # Base template
│       ├── index.html                  # Main collage page
│       ├── cart.html                   # Shopping cart page
│       └── detail.html                 # Detail view page
├── ingest/
│   ├── discogs_seller_export.py        # Script to export Discogs data
│   ├── discogs_seller_listings.csv     # CSV data file
│   └── discogs_seller_export_example_usage.sh
├── config.py           # Application configuration
├── run.py              # Flask application entry point
├── requirements.txt    # Python dependencies
├── start_server.sh     # Quick start script
└── README.md           # This file
```

## 🛠️ How It Works

1. **Server**: Reads the Discogs CSV file and serves it as JSON via `/api/data`
2. **Frontend**: Fetches the data and creates a responsive grid of vinyl images
3. **Images**: Displays actual Discogs vinyl cover images from the `image_uri` field
4. **Fallback**: Shows "No Image" placeholder for items without images

## 📊 Data Requirements

The server automatically looks for CSV files with names like:
- `discogs_seller_listings.csv`
- `discogs_seller_listings_*.csv`

It will use the most recent file found in the `ingest/` directory.

## 🎨 Customization

You can customize the appearance by editing the SCSS files in `app/static/scss/`:
- **`_variables.scss`**: Change colors, fonts, and other design tokens
- **`main.scss`**: Modify the main page layout and styling
- **`cart.scss`**: Customize the shopping cart appearance
- **`detail.scss`**: Adjust the detail view styling
- **`_vinyl.scss`**: Change vinyl item display

The SCSS files are automatically compiled to CSS when the Flask app starts.

## 🔧 Troubleshooting

**Server won't start?**
- Make sure port 3000 is available
- Check that you have a Discogs CSV file in the `ingest/` directory

**No images showing?**
- Verify the CSV file has `image_uri` data
- Check browser console for image loading errors

**Data not loading?**
- Ensure the CSV file is properly formatted
- Check server logs for errors

## 📱 Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## 🎯 Features in Detail

### Visual Collage
- Responsive grid that adapts to screen size
- Hover effects with scaling and shadows
- Lazy loading for better performance
- Fallback for missing images

### Statistics Panel
- Total number of vinyl items
- Count of items with images
- Average price calculation
- Total collection value

### Interactive Elements
- Click any vinyl to see full details
- Smooth scrolling with visual indicators
- Responsive design for all devices

Enjoy exploring your vinyl collection! 🎵
