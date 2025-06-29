#!/usr/bin/env python3
"""
Test script to generate traffic for FastAPI monitoring demo.
This script helps test the monitoring setup by making requests to various endpoints.
"""

import asyncio
import httpx
import random
import time
from typing import List

BASE_URL = "http://localhost:8000"

async def test_endpoint(client: httpx.AsyncClient, endpoint: str, method: str = "GET", **kwargs):
    """Test a single endpoint and return response info."""
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{endpoint}", **kwargs)
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "success": response.status_code < 400
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "error",
            "error": str(e),
            "success": False
        }

async def generate_traffic(duration_seconds: int = 60, requests_per_second: int = 2):
    """Generate traffic to the FastAPI application."""
    
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/api/users/123", "GET"),
        ("/api/users/456", "GET"),
        ("/api/users/789", "GET"),
        ("/api/users/404", "GET"),  # This will generate 404 errors
        ("/api/users", "POST"),
        ("/api/simulate-error", "GET"),  # This will generate random errors
    ]
    
    print(f"🚀 Starting traffic generation for {duration_seconds} seconds")
    print(f"📊 Target: {requests_per_second} requests per second")
    print(f"🎯 Endpoints: {len(endpoints)} different endpoints")
    print("-" * 50)
    
    start_time = time.time()
    total_requests = 0
    successful_requests = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        while time.time() - start_time < duration_seconds:
            # Select random endpoint
            endpoint, method = random.choice(endpoints)
            
            # Make request
            result = await test_endpoint(client, endpoint, method)
            total_requests += 1
            
            if result["success"]:
                successful_requests += 1
            
            # Print progress every 10 requests
            if total_requests % 10 == 0:
                elapsed = time.time() - start_time
                rate = total_requests / elapsed if elapsed > 0 else 0
                success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
                
                print(f"⏱️  {elapsed:.1f}s | 📈 {rate:.1f} req/s | ✅ {success_rate:.1f}% success | Total: {total_requests}")
            
            # Sleep to control rate
            await asyncio.sleep(1.0 / requests_per_second)
    
    # Final statistics
    elapsed = time.time() - start_time
    actual_rate = total_requests / elapsed if elapsed > 0 else 0
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    
    print("\n" + "=" * 50)
    print("📊 FINAL STATISTICS")
    print("=" * 50)
    print(f"Duration: {elapsed:.1f} seconds")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {total_requests - successful_requests}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Actual rate: {actual_rate:.1f} requests/second")
    print("=" * 50)

async def test_all_endpoints():
    """Test all endpoints once to verify they're working."""
    print("🔍 Testing all endpoints...")
    
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/api/users/123", "GET"),
        ("/api/users", "POST"),
        ("/api/simulate-error", "GET"),
        ("/metrics", "GET"),
        ("/custom-metrics", "GET"),
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint, method in endpoints:
            result = await test_endpoint(client, endpoint, method)
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {method:4} {endpoint:20} -> {result['status']}")

async def main():
    """Main function to run the test script."""
    print("FastAPI Monitoring Test Script")
    print("=" * 40)
    
    # Test if the API is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ FastAPI is running!")
            else:
                print(f"⚠️  FastAPI returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to FastAPI at {BASE_URL}")
        print(f"Error: {e}")
        print("\nMake sure FastAPI is running:")
        print("docker-compose up --build")
        return
    
    print("\nChoose an option:")
    print("1. Test all endpoints once")
    print("2. Generate light traffic (1 req/s for 30s)")
    print("3. Generate moderate traffic (2 req/s for 60s)")
    print("4. Generate heavy traffic (5 req/s for 120s)")
    print("5. Custom traffic generation")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        await test_all_endpoints()
    elif choice == "2":
        await generate_traffic(duration_seconds=30, requests_per_second=1)
    elif choice == "3":
        await generate_traffic(duration_seconds=60, requests_per_second=2)
    elif choice == "4":
        await generate_traffic(duration_seconds=120, requests_per_second=5)
    elif choice == "5":
        try:
            duration = int(input("Duration in seconds: "))
            rate = float(input("Requests per second: "))
            await generate_traffic(duration_seconds=duration, requests_per_second=rate)
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    else:
        print("❌ Invalid choice.")
    
    print("\n🎉 Test completed!")
    print("📊 Check your monitoring dashboards:")
    print("   - Prometheus: http://localhost:9090")
    print("   - Grafana: http://localhost:3000 (admin/admin)")

if __name__ == "__main__":
    asyncio.run(main()) 