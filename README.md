<img width="1177" height="1019" alt="image" src="https://github.com/user-attachments/assets/21ce844f-067a-4413-9b12-cd1525e8b220" />
<img width="1179" height="1019" alt="image" src="https://github.com/user-attachments/assets/c0d51d73-59ac-48dd-af09-1582769f7c93" />
<img width="1183" height="1025" alt="image" src="https://github.com/user-attachments/assets/70ed6de1-f5ea-4c72-bf34-1028b3d841ba" />


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

1. **Make sure you have a Discogs CSV file** (run `discogs_seller_export.py` first)

2. **Start the server**:
   ```bash
   python3 server.py
   ```

3. **Open your browser** and visit:
   ```
   http://localhost:3000
   ```

## 📁 File Structure

```
discogs_image_collage/
├── index.html          # Main web page with collage
├── server.py           # Python web server
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

It will use the most recent file found in the current directory.

## 🎨 Customization

You can customize the appearance by editing the CSS in `index.html`:
- Change colors in the `body` background gradient
- Modify grid layout in `.collage-grid`
- Adjust vinyl item styling in `.vinyl-item`

## 🔧 Troubleshooting

**Server won't start?**
- Make sure port 3000 is available
- Check that you have a Discogs CSV file in the current directory

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
