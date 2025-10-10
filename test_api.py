#!/usr/bin/env python3
"""
Simple test script for Freakinbeats API endpoints.

Tests the REST API to ensure it's working correctly.
"""

import requests
import json
import sys


def test_api_stats():
    """Test the /api/stats endpoint."""
    url = "http://localhost:3000/api/stats"
    
    print("=" * 60)
    print("🧪 Testing Freakinbeats API")
    print("=" * 60)
    print(f"\n📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type')}")
        print("\n📊 Response Data:")
        print("-" * 60)
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            if 'total_listings' in data:
                print("\n" + "=" * 60)
                print(f"✅ SUCCESS: Found {data['total_listings']} listings in database")
                if data.get('last_updated'):
                    print(f"📅 Last Updated: {data['last_updated']}")
                print("=" * 60)
                return True
            else:
                print("\n❌ ERROR: Response missing 'total_listings' field")
                return False
        else:
            print(f"\n❌ ERROR: Unexpected status code {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running: python3 run.py")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_api_data():
    """Test the /api/data endpoint."""
    url = "http://localhost:3000/api/data"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Received {len(data)} listings")
            
            if len(data) > 0:
                print("\n📀 Sample listing:")
                print("-" * 60)
                sample = data[0]
                print(f"Title: {sample.get('release_title')}")
                print(f"Artist: {sample.get('primary_artist')}")
                print(f"Price: {sample.get('price_value')} {sample.get('price_currency')}")
                print(f"Condition: {sample.get('condition')}")
                print("-" * 60)
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_api_search():
    """Test the /api/search endpoint."""
    url = "http://localhost:3000/api/search?q=DJ"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search returned {len(data)} results")
            
            if len(data) > 0:
                print("\n🔍 Sample search result:")
                print("-" * 60)
                sample = data[0]
                print(f"Title: {sample.get('release_title')}")
                print(f"Artist: {sample.get('primary_artist')}")
                print(f"Price: {sample.get('price_value')} {sample.get('price_currency')}")
                print("-" * 60)
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all API tests."""
    print("\n🎵 Freakinbeats API Test Suite")
    
    results = []
    
    # Test stats endpoint
    results.append(("Stats Endpoint", test_api_stats()))
    
    # Test data endpoint
    results.append(("Data Endpoint", test_api_data()))
    
    # Test search endpoint
    results.append(("Search Endpoint", test_api_search()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"Results: {total_passed}/{total_tests} tests passed")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if total_passed == total_tests else 1)


if __name__ == "__main__":
    main()

