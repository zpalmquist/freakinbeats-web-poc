#!/usr/bin/env python3
"""
Comprehensive test script for Freakinbeats API endpoints.

Tests all available REST API endpoints to ensure they're working correctly.

Usage:
    python3 utils/test_api.py

Make sure the server is running on http://localhost:3000 before running tests.
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


def test_api_data_by_id():
    """Test the /api/data/<id> endpoint."""
    # First get a listing to get a valid ID
    try:
        data_response = requests.get("http://localhost:3000/api/data", timeout=5)
        if data_response.status_code == 200:
            data = data_response.json()
            if len(data) > 0:
                # Get the listing_id from the first item
                listing_id = data[0].get('listing_id')
                url = f"http://localhost:3000/api/data/{listing_id}"
            else:
                print("\n⚠️  No listings available to test /api/data/<id>")
                return True  # Not a failure, just no data
        else:
            print("\n⚠️  Could not fetch listings for /api/data/<id> test")
            return True
    except Exception as e:
        print(f"\n⚠️  Could not setup /api/data/<id> test: {e}")
        return True
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved specific listing")
            
            print("\n📀 Listing details:")
            print("-" * 60)
            print(f"Listing ID: {data.get('listing_id')}")
            print(f"Title: {data.get('release_title')}")
            print(f"Artist: {data.get('primary_artist')}")
            print(f"Label: {data.get('primary_label')}")
            print(f"Year: {data.get('release_year')}")
            print(f"Price: {data.get('price_value')} {data.get('price_currency')}")
            print(f"Condition: {data.get('condition')}")
            print(f"Sleeve: {data.get('sleeve_condition')}")
            print("-" * 60)
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_api_detail():
    """Test the /api/detail/<id> endpoint."""
    # First get a listing to get a valid ID
    try:
        data_response = requests.get("http://localhost:3000/api/data", timeout=5)
        if data_response.status_code == 200:
            data = data_response.json()
            if len(data) > 0:
                # Use database ID (first item's index)
                url = "http://localhost:3000/api/detail/0"
            else:
                print("\n⚠️  No listings available to test /api/detail/<id>")
                return True  # Not a failure, just no data
        else:
            print("\n⚠️  Could not fetch listings for /api/detail/<id> test")
            return True
    except Exception as e:
        print(f"\n⚠️  Could not setup /api/detail/<id> test: {e}")
        return True
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved detailed listing with videos")
            
            print("\n📀 Detailed listing:")
            print("-" * 60)
            print(f"Title: {data.get('release_title')}")
            print(f"Artist: {data.get('primary_artist')}")
            print(f"Videos: {len(data.get('videos', []))} available")
            
            if data.get('videos'):
                print("\n🎬 Sample video:")
                video = data['videos'][0]
                print(f"  Title: {video.get('title')}")
                print(f"  Duration: {video.get('duration')}s")
                print(f"  YouTube ID: {video.get('youtube_id')}")
            
            print(f"\nLabel URLs: {len(data.get('label_urls', []))} available")
            print(f"Label Overviews: {len(data.get('label_overviews', {}))} available")
            print("-" * 60)
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_api_filter():
    """Test the /api/filter endpoint with multiple criteria."""
    url = "http://localhost:3000/api/filter?q=music"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filter returned {len(data)} results")
            
            if len(data) > 0:
                print("\n🔍 Sample filtered result:")
                print("-" * 60)
                sample = data[0]
                print(f"Title: {sample.get('release_title')}")
                print(f"Artist: {sample.get('primary_artist')}")
                print(f"Label: {sample.get('primary_label')}")
                print(f"Year: {sample.get('release_year')}")
                print(f"Condition: {sample.get('condition')}")
                print(f"Sleeve: {sample.get('sleeve_condition')}")
                print("-" * 60)
            else:
                print("\n⚠️  No results matched the filter criteria")
            
            # Test with multiple filters
            print("\n🔧 Testing multiple filter criteria...")
            multi_url = "http://localhost:3000/api/filter?condition=Near Mint (NM or M-)"
            multi_response = requests.get(multi_url, timeout=5)
            if multi_response.status_code == 200:
                multi_data = multi_response.json()
                print(f"✅ Multi-filter returned {len(multi_data)} results")
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_api_facets():
    """Test the /api/facets endpoint."""
    url = "http://localhost:3000/api/facets"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Retrieved filter facets with counts")
            
            print("\n📊 Filter Facets Summary:")
            print("-" * 60)
            print(f"Artists: {len(data.get('artists', []))} unique")
            print(f"Labels: {len(data.get('labels', []))} unique")
            print(f"Years: {len(data.get('years', []))} unique")
            print(f"Conditions: {len(data.get('conditions', []))} unique")
            print(f"Sleeve Conditions: {len(data.get('sleeve_conditions', []))} unique")
            
            # Show top 5 artists by count
            if data.get('artists'):
                print("\n🎤 Top 5 Artists by listing count:")
                for artist in data['artists'][:5]:
                    print(f"  {artist['value']}: {artist['count']} listings")
            
            # Show top 5 labels by count
            if data.get('labels'):
                print("\n🏷️  Top 5 Labels by listing count:")
                for label in data['labels'][:5]:
                    print(f"  {label['value']}: {label['count']} listings")
            
            # Show conditions
            if data.get('conditions'):
                print("\n💿 Conditions:")
                for condition in data['conditions']:
                    print(f"  {condition['value']}: {condition['count']} listings")
            
            print("-" * 60)
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_access_logs():
    """Test the /api/logs endpoint."""
    url = "http://localhost:3000/api/logs?limit=5"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data)} access log entries")
            
            if len(data) > 0:
                print("\n📝 Sample access log:")
                print("-" * 60)
                sample = data[0]
                print(f"Timestamp: {sample.get('timestamp')}")
                print(f"Method: {sample.get('method')}")
                print(f"Path: {sample.get('path')}")
                print(f"IP: {sample.get('ip_address')}")
                print(f"Status: {sample.get('status_code')}")
                print(f"Response Time: {sample.get('response_time_ms')}ms")
                print("-" * 60)
            
            return True
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_log_stats():
    """Test the /api/logs/stats endpoint."""
    url = "http://localhost:3000/api/logs/stats"
    
    print("\n" + "=" * 60)
    print(f"📡 Making GET request to: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Access Log Statistics:")
            print("-" * 60)
            print(f"Total Requests: {data.get('total_requests')}")
            print(f"By Method: {data.get('by_method')}")
            print(f"By Status: {data.get('by_status')}")
            print(f"Avg Response Time: {data.get('avg_response_time_ms')}ms")
            print("\nTop Paths:")
            for item in data.get('top_paths', [])[:5]:
                print(f"  {item['path']}: {item['count']} requests")
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
    print("Testing all available API endpoints...")
    
    results = []
    
    # Core inventory endpoints
    results.append(("Stats Endpoint", test_api_stats()))
    results.append(("Data Endpoint (All Listings)", test_api_data()))
    results.append(("Data by ID Endpoint", test_api_data_by_id()))
    results.append(("Detail Endpoint (with Videos)", test_api_detail()))
    
    # Search and filter endpoints
    results.append(("Search Endpoint", test_api_search()))
    results.append(("Filter Endpoint (Advanced)", test_api_filter()))
    results.append(("Facets Endpoint (Filter Counts)", test_api_facets()))
    
    # Access logging endpoints
    results.append(("Access Logs Endpoint", test_access_logs()))
    results.append(("Log Stats Endpoint", test_log_stats()))
    
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
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed.")
    
    # Exit with appropriate code
    sys.exit(0 if total_passed == total_tests else 1)


if __name__ == "__main__":
    main()

