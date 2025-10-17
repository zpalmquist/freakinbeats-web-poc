#!/bin/bash
# Restart Freakinbeats server with clean CSS compilation

echo "🛑 Stopping server..."
pkill -f "python.*run.py" 2>/dev/null || true
sleep 0.5

echo "🧹 Cleaning generated CSS files..."
rm -rf app/static/css/*.css
rm -rf app/static/.webassets-cache

echo "🔨 Starting server (will compile SCSS)..."
python3 run.py
