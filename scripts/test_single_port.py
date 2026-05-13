#!/usr/bin/env python3
"""
Test script to verify CogniForge single-port architecture.
This script tests the Nginx reverse proxy configuration and service health.
"""

import requests
import time
import json
import sys
from typing import Dict, Any

def test_endpoint(url: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint."""
    try:
        response = requests.get(url, timeout=10)
        return {
            "url": url,
            "status_code": response.status_code,
            "success": response.status_code == expected_status,
            "response_time": response.elapsed.total_seconds(),
            "content_type": response.headers.get("content-type", ""),
            "data": response.json() if "application/json" in response.headers.get("content-type", "") else None
        }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status_code": None,
            "success": False,
            "error": str(e),
            "response_time": None,
            "content_type": None,
            "data": None
        }

def run_tests(base_url: str = "http://localhost:3000"):
    """Run comprehensive tests on the single-port architecture."""
    
    print("🧪 Testing CogniForge Single-Port Architecture")
    print("=" * 50)
    
    tests = [
        ("Nginx Health Check", f"{base_url}/health"),
        ("Backend Health Check", f"{base_url}/api/health"),
        ("API Root", f"{base_url}/api"),
        ("API Version", f"{base_url}/api/version"),
        ("System Info", f"{base_url}/api/system/info"),
        ("API Documentation", f"{base_url}/api/docs"),
    ]
    
    results = []
    all_passed = True
    
    for test_name, url in tests:
        print(f"\n🔍 Testing: {test_name}")
        print(f"   URL: {url}")
        
        result = test_endpoint(url)
        
        if result["success"]:
            print(f"   ✅ PASS - Status: {result['status_code']}, Time: {result['response_time']:.3f}s")
            if result["data"]:
                # Print relevant info from response
                if "status" in result["data"]:
                    print(f"   📊 Status: {result['data']['status']}")
                if "version" in result["data"]:
                    print(f"   📦 Version: {result['data']['version']}")
        else:
            print(f"   ❌ FAIL - Status: {result.get('status_code', 'N/A')}")
            if "error" in result:
                print(f"   💥 Error: {result['error']}")
            all_passed = False
        
        results.append((test_name, result))
    
    # Test WebSocket endpoint (basic connectivity)
    print(f"\n🔍 Testing: WebSocket Endpoint")
    print(f"   URL: {base_url.replace('http', 'ws')}/ws")
    # Note: WebSocket testing requires a WebSocket client
    print("   ⚠️  WebSocket test requires manual verification")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r["success"])
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all_passed:
        print("\n🎉 All tests passed! Single-port architecture is working correctly.")
        print("\n🌐 Access points:")
        print(f"   Frontend: {base_url}")
        print(f"   API Docs: {base_url}/api/docs")
        print(f"   Health: {base_url}/health")
        print(f"   API Health: {base_url}/api/health")
    else:
        print("\n⚠️  Some tests failed. Check service logs with: docker-compose logs -f")
        sys.exit(1)
    
    return all_passed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CogniForge single-port architecture")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL to test")
    parser.add_argument("--wait", type=int, default=10, help="Seconds to wait before testing")
    
    args = parser.parse_args()
    
    print(f"⏳ Waiting {args.wait} seconds for services to start...")
    time.sleep(args.wait)
    
    success = run_tests(args.url)
    
    if success:
        print("\n🚀 CogniForge is ready! Open your browser to:", args.url)
    else:
        print("\n🔧 Check the following:")
        print("   1. Are Docker services running? (docker-compose ps)")
        print("   2. Check service logs: docker-compose logs -f")
        print("   3. Verify port 3000 is available")
        sys.exit(1)
