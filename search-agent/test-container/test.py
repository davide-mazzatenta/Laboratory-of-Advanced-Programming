#!/usr/bin/env python3
"""
Simple test for Search Agent via API Gateway
Tests the Italian legal query as requested
"""

import requests
import json

def test_search_agent():
    """Test search agent via API Gateway"""
    
    # API Gateway URL (where orchestrator would call)
    gateway_url = "http://localhost:8080"
    
    # Test query - Italian legal search
    query = "cerca ultime sentenze su violenza sui minori corte di cassazione"
    
    print("🧪 Testing Search Agent via API Gateway")
    print("=" * 60)
    print(f"📝 Query: {query}")
    print(f"🌐 Gateway URL: {gateway_url}/api/v1/search")
    print("=" * 60)
    
    # Prepare request payload
    payload = {
        "query": query,
        "max_results": 5,
        "include_sources": True
    }
    
    try:
        print("📡 Sending request...")
        
        # Make request to API Gateway (as orchestrator would)
        response = requests.post(
            f"{gateway_url}/api/v1/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Search + AI can take time
        )
        
        print(f"📈 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Search completed successfully!")
            print("=" * 60)
            print("📋 RESULTS:")
            print("=" * 60)
            
            print(f"🔧 Search providers used: {result.get('search_providers_used', [])}")
            print(f"🔗 Sources found: {len(result.get('sources', []))}")
            print(f"📝 Summary length: {len(result.get('summary', ''))} characters")
            
            print("\n" + "=" * 60)
            print("📄 AI SUMMARY:")
            print("=" * 60)
            print(result.get('summary', 'No summary available'))
            
            print("\n" + "=" * 60)
            print("🔗 SOURCES:")
            print("=" * 60)
            for i, source in enumerate(result.get('sources', []), 1):
                print(f"{i}. {source.get('title', 'No title')}")
                print(f"   URL: {source.get('url', 'No URL')}")
                print(f"   Snippet: {source.get('snippet', 'No snippet')[:100]}...")
                print()
            
            return True
            
        else:
            print(f"❌ Search failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (this is normal for first AI model request)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure services are running:")
        print("   docker-compose up search-agent api-gateway")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_status():
    """Test status endpoint"""
    gateway_url = "http://localhost:8080"
    
    print("\n📊 Testing status endpoint...")
    
    try:
        response = requests.get(f"{gateway_url}/api/v1/search/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Status endpoint working!")
            print(f"Status: {json.dumps(status, indent=2)}")
            return True
        else:
            print(f"❌ Status failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Search Agent Integration Test")
    print("Calling search-agent via API Gateway (as orchestrator would)")
    print()
    
    # Run the search test
    search_success = test_search_agent()
    
    # Run the status test
    status_success = test_status()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if search_success and status_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Search Agent is working correctly via API Gateway")
    else:
        print("❌ SOME TESTS FAILED")
        if not search_success:
            print("   - Search functionality failed")
        if not status_success:
            print("   - Status endpoint failed")
        
        print("\n💡 Troubleshooting:")
        print("   1. Check if services are running: docker-compose ps")
        print("   2. Check logs: docker-compose logs search-agent api-gateway")
        print("   3. Verify API keys in search_agent.py")
        print("   4. Test direct: curl http://localhost:8002/health")