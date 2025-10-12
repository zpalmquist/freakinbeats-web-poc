#!/usr/bin/env python3
"""
Test Discogs API Token

This utility script tests if a Discogs API token is valid by making
a simple API call and displaying the results.

Usage:
    python3 utils/test_discogs_token.py
    python3 utils/test_discogs_token.py --token YOUR_TOKEN_HERE
    python3 utils/test_discogs_token.py --username your_username
"""

import argparse
import os
import sys
import requests
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_env_token():
    """Load token from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('DISCOGS_TOKEN'), os.getenv('DISCOGS_SELLER_USERNAME')
    except ImportError:
        # Try reading .env file manually
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            token = None
            username = None
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DISCOGS_TOKEN='):
                        token = line.split('=', 1)[1].strip()
                    elif line.startswith('DISCOGS_SELLER_USERNAME='):
                        username = line.split('=', 1)[1].strip()
            return token, username
        return None, None


def test_token(token, username=None):
    """
    Test if a Discogs API token is valid.
    
    Args:
        token: Discogs personal access token
        username: Optional username to test inventory access
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    print("=" * 70)
    print("🧪 Testing Discogs API Token")
    print("=" * 70)
    
    if not token:
        print("❌ No token provided")
        return False
    
    print(f"\n📋 Token Info:")
    print(f"   Length: {len(token)} characters")
    print(f"   Preview: {token[:10]}...{token[-5:]}")
    
    # Test 1: Check identity endpoint (doesn't require username)
    print(f"\n1️⃣  Testing Token Validity...")
    headers = {
        'User-Agent': 'FreakinbeatsWebApp/1.0',
        'Authorization': f'Discogs token={token}'
    }
    
    try:
        response = requests.get('https://api.discogs.com/oauth/identity', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Token is VALID!")
            print(f"   Username: {data.get('username', 'N/A')}")
            print(f"   ID: {data.get('id', 'N/A')}")
            print(f"   Resource URL: {data.get('resource_url', 'N/A')}")
            
            # Use the username from identity if not provided
            if not username:
                username = data.get('username')
            
        elif response.status_code == 401:
            print(f"   ❌ Token is INVALID")
            print(f"   Error: {response.json().get('message', 'Authentication failed')}")
            return False
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing token: {e}")
        return False
    
    # Test 2: Check rate limits
    print(f"\n2️⃣  Checking Rate Limits...")
    try:
        rate_limit = response.headers.get('X-Discogs-Ratelimit', 'Unknown')
        rate_remaining = response.headers.get('X-Discogs-Ratelimit-Remaining', 'Unknown')
        
        print(f"   Requests per minute: {rate_limit}")
        print(f"   Remaining: {rate_remaining}")
        
    except Exception as e:
        print(f"   ⚠️  Could not read rate limits: {e}")
    
    # Test 3: Test inventory access if username provided
    if username:
        print(f"\n3️⃣  Testing Inventory Access for '{username}'...")
        try:
            inventory_url = f'https://api.discogs.com/users/{username}/inventory'
            response = requests.get(
                inventory_url, 
                headers=headers,
                params={'per_page': 1}
            )
            
            if response.status_code == 200:
                data = response.json()
                pagination = data.get('pagination', {})
                total_items = pagination.get('items', 0)
                
                print(f"   ✅ Inventory access: SUCCESS")
                print(f"   Total listings: {total_items}")
                
                if total_items > 0:
                    print(f"   Pages: {pagination.get('pages', 0)}")
                    print(f"   Per page: {pagination.get('per_page', 0)}")
                else:
                    print(f"   ⚠️  No listings found (inventory may be empty)")
                    
            elif response.status_code == 404:
                print(f"   ❌ User not found: {username}")
                print(f"   Make sure the username is correct")
                return False
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                print(f"   {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error accessing inventory: {e}")
            return False
    else:
        print(f"\n3️⃣  Skipping Inventory Test (no username provided)")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("✅ Token Test Complete - Token is VALID and working!")
    print("=" * 70)
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Discogs API token validity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test token from .env file
  python3 utils/test_discogs_token.py
  
  # Test specific token
  python3 utils/test_discogs_token.py --token YOUR_TOKEN_HERE
  
  # Test token with specific username
  python3 utils/test_discogs_token.py --username freakin_beats
        """
    )
    
    parser.add_argument(
        '--token',
        help='Discogs API token to test (if not provided, loads from .env)'
    )
    parser.add_argument(
        '--username',
        help='Discogs username to test inventory access'
    )
    
    args = parser.parse_args()
    
    # Get token
    if args.token:
        token = args.token
        username = args.username
    else:
        print("📁 Loading token from .env file...")
        token, username = load_env_token()
        
        if args.username:
            username = args.username
    
    if not token:
        print("\n❌ No token found!")
        print("\nOptions:")
        print("  1. Set DISCOGS_TOKEN in .env file")
        print("  2. Pass token with --token argument")
        print(f"\nGet a token from: https://www.discogs.com/settings/developers")
        sys.exit(1)
    
    # Test the token
    success = test_token(token, username)
    
    if not success:
        print("\n💡 Need a new token?")
        print("   Visit: https://www.discogs.com/settings/developers")
        print("   Generate a 'Personal Access Token'")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()

