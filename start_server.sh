#!/bin/bash
# Quick start script for Freakinbeats Web Application

echo "======================================"
echo "🎵 Freakinbeats Server Startup"
echo "======================================"
echo ""

# Check if DISCOGS_TOKEN is set
if [ -z "$DISCOGS_TOKEN" ]; then
    echo "⚠️  WARNING: DISCOGS_TOKEN environment variable not set!"
    echo ""
    echo "To enable automatic Discogs sync, set your token:"
    echo "  export DISCOGS_TOKEN='your_token_here'"
    echo "  export DISCOGS_SELLER_USERNAME='your_username'"
    echo ""
    echo "Get your token from: https://www.discogs.com/settings/developers"
    echo ""
    echo "The server will start, but auto-sync will be disabled."
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to cancel..."
else
    echo "✅ DISCOGS_TOKEN is set"
    echo "✅ Seller: ${DISCOGS_SELLER_USERNAME:-freakin_beats}"
    echo ""
fi

# Kill any existing server processes
echo "🔍 Checking for existing server processes..."
pkill -f "python.*run.py" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 1

# Start the server
echo ""
echo "🚀 Starting Freakinbeats server..."
echo "======================================"
echo ""
python3 run.py

# When stopped
trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo "🛑 Stopping server..."
    pkill -f "python.*run.py" 2>/dev/null || true
    exit 0
}
