#!/bin/bash
# Example usage of the Discogs Seller Export Script

echo "=== Discogs Seller Export Examples ==="
echo ""

echo "1. Basic usage (requires DISCOGS_TOKEN environment variable):"
echo "   export DISCOGS_TOKEN='your_token_here'"
echo "   python3 discogs_seller_export.py --seller freakin_beats"
echo ""

echo "2. With custom output file:"
echo "   python3 discogs_seller_export.py --seller freakin_beats --output freakin_beats_listings.csv"
echo ""

echo "3. With token as command line argument:"
echo "   python3 discogs_seller_export.py --seller freakin_beats --token your_token_here"
echo ""

echo "4. Limit to first 5 pages (for testing):"
echo "   python3 discogs_seller_export.py --seller freakin_beats --max-pages 5"
echo ""

echo "5. Full example with all options:"
echo "   python3 discogs_seller_export.py --seller freakin_beats --token your_token_here --output my_listings.csv --max-pages 10"
echo ""

echo "=== CSV Output Fields ==="
echo "The script exports ALL available fields including:"
echo "- Basic listing info (ID, status, condition, price, shipping)"
echo "- Seller information (username, rating, location)"
echo "- Release details (title, artist, label, format, year)"
echo "- Music metadata (genres, styles, country, catalog number)"
echo "- Images and statistics"
echo "- Export timestamp"
echo ""

echo "=== Getting Your Discogs Token ==="
echo "1. Go to: https://www.discogs.com/settings/developers"
echo "2. Click 'Generate new token'"
echo "3. Copy the token and use it as shown above"
echo ""
