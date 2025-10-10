#!/usr/bin/env python3
"""
Discogs Image Collage Web Server

A simple web server that reads the Discogs seller CSV file and serves
a beautiful collage of all vinyl record images.

Usage:
    python3 server.py
    Then visit: http://localhost:3000
"""

import http.server
import socketserver
import json
import csv
import os
import sys
from urllib.parse import urlparse, parse_qs
import mimetypes
from pathlib import Path

class DiscogsCollageHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the Discogs collage web server."""
    
    def __init__(self, *args, **kwargs):
        # Set the CSV file path (look for it in current directory)
        self.csv_file = self.find_csv_file()
        super().__init__(*args, **kwargs)
    
    def find_csv_file(self):
        """Find the Discogs CSV file in the current directory."""
        current_dir = Path(__file__).parent
        csv_files = list(current_dir.glob("discogs_seller_listings*.csv"))
        
        if csv_files:
            # Return the most recent CSV file
            return max(csv_files, key=os.path.getmtime)
        else:
            return None
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/data':
            self.serve_csv_data()
        elif parsed_path.path == '/':
            self.serve_index()
        elif parsed_path.path == '/cart':
            self.serve_cart()
        elif parsed_path.path.startswith('/detail/'):
            self.serve_detail()
        else:
            # Serve static files
            super().do_GET()
    
    def serve_index(self):
        """Serve the main HTML page."""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "index.html not found")
        except Exception as e:
            self.send_error(500, f"Error serving index: {str(e)}")
    
    def serve_csv_data(self):
        """Serve CSV data as JSON."""
        try:
            if not self.csv_file or not os.path.exists(self.csv_file):
                self.send_error(404, "CSV file not found")
                return
            
            # Read CSV data
            data = []
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean up the data
                    cleaned_row = {}
                    for key, value in row.items():
                        # Convert empty strings to None for JSON
                        cleaned_row[key] = value if value.strip() else None
                    data.append(cleaned_row)
            
            # Send JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            self.wfile.write(json_data.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error reading CSV: {str(e)}")
    
    def serve_cart(self):
        """Serve the cart page."""
        try:
            with open('cart.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "cart.html not found")
        except Exception as e:
            self.send_error(500, f"Error serving cart: {str(e)}")
    
    def serve_detail(self):
        """Serve the detail page."""
        try:
            with open('detail.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "detail.html not found")
        except Exception as e:
            self.send_error(500, f"Error serving detail: {str(e)}")
    
    def log_message(self, format, *args):
        """Custom log format."""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")

def main():
    """Start the web server."""
    PORT = 3000
    
    # Check if CSV file exists
    current_dir = Path(__file__).parent
    csv_files = list(current_dir.glob("discogs_seller_listings*.csv"))
    
    if not csv_files:
        print("❌ No Discogs CSV file found!")
        print(f"Looking in: {current_dir}")
        print("Please run the discogs_seller_export.py script first to generate the CSV file.")
        sys.exit(1)
    
    csv_file = max(csv_files, key=os.path.getmtime)
    print(f"📁 Using CSV file: {csv_file}")
    print(f"📊 File size: {os.path.getsize(csv_file) / 1024:.1f} KB")
    
    # Count rows in CSV
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_count = sum(1 for row in reader) - 1  # Subtract header
        print(f"🎵 Found {row_count} vinyl listings")
    except Exception as e:
        print(f"⚠️  Could not count rows: {e}")
    
    # Start server
    try:
        with socketserver.TCPServer(("", PORT), DiscogsCollageHandler) as httpd:
            print(f"🚀 Discogs Image Collage Server")
            print(f"🌐 Server running at: http://localhost:{PORT}")
            print(f"📱 Open your browser and visit the URL above")
            print(f"⏹️  Press Ctrl+C to stop the server")
            print("=" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print("Try closing other applications or use a different port.")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
