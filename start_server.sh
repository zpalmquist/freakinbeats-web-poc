#!/bin/bash
# Quick start script for Discogs Image Collage Server

echo "🎵 Discogs Vinyl Collection Collage"
echo "=================================="
echo ""

# Check if CSV file exists
if [ ! -f "discogs_seller_listings.csv" ]; then
    echo "❌ No Discogs CSV file found!"
    echo "Please run the discogs_seller_export.py script first."
    echo ""
    echo "To export your data:"
    echo "  cd .."
    echo "  python3 discogs_seller_export.py --seller freakin_beats"
    exit 1
fi

echo "✅ Found Discogs CSV file"
echo "🚀 Starting server..."
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 simple_server.py
