#!/usr/bin/env python3
"""
Test script for Smart Traffic Management System Backend
Run this script to test all API endpoints and functionality
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_VIDEO_PATH = "test_video.mp4"  # Create a small test video or use dummy mode

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   YOLO Available: {data['yolo_available']}")
            print(f"   Mode: {data['mode']}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running")
        return False

def test_traffic_data():
    """Test traffic data endpoint"""
    print("\n🔍 Testing Traffic Data...")
    try:
        response = requests.get(f"{BASE_URL}/traffic_data")
        if response.status_code == 200:
            data = response.json()
            print("✅ Traffic Data Retrieved:")
            for lane, info in data['data'].items():
                print(f"   {lane}: {info['count']} vehicles, {info['signal']} ({info['time']}s)")
            return True
        else:
            print(f"❌ Traffic Data Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_processing_status():
    """Test processing status endpoint"""
    print("\n🔍 Testing Processing Status...")
    try:
        response = requests.get(f"{BASE_URL}/processing_status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Processing Status: {data['status']} ({data['progress']}%)")
            return True
        else:
            print(f"❌ Processing Status Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_simulate_traffic():
    """Test traffic simulation endpoint"""
    print("\n🔍 Testing Traffic Simulation...")
    try:
        # Test updating lane A
        test_data = {"lane": "A", "count": 18}
        response = requests.post(
            f"{BASE_URL}/simulate_traffic",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Traffic Simulation: {data['message']}")
            print(f"   Lane A now has {data['data']['laneA']['count']} vehicles")
            return True
        else:
            print(f"❌ Traffic Simulation Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_reset_signals():
    """Test reset signals endpoint"""
    print("\n🔍 Testing Reset Signals...")
    try:
        response = requests.post(f"{BASE_URL}/reset_signals")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reset Signals: {data['message']}")
            return True
        else:
            print(f"❌ Reset Signals Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_video_processing():
    """Test video processing endpoint (if test video exists)"""
    print("\n🔍 Testing Video Processing...")
    
    if not os.path.exists(TEST_VIDEO_PATH):
        print(f"⚠️  Test video not found: {TEST_VIDEO_PATH}")
        print("   Skipping video processing test")
        return True
    
    try:
        with open(TEST_VIDEO_PATH, 'rb') as video_file:
            files = {'video': video_file}
            print("   Uploading test video...")
            
            response = requests.post(f"{BASE_URL}/process_video", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print("✅ Video Processing Successful:")
                    print(f"   Processed {data['processed_frames']} frames")
                    print(f"   Vehicle counts: {data['vehicle_counts']}")
                    return True
                else:
                    print(f"❌ Video Processing Failed: {data['message']}")
                    return False
            else:
                print(f"❌ Video Processing HTTP Error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_processed_frames():
    """Test processed frames endpoint"""
    print("\n🔍 Testing Processed Frames...")
    try:
        response = requests.get(f"{BASE_URL}/get_processed_frames")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Processed Frames: {data['count']} frames available")
            return True
        else:
            print(f"❌ Processed Frames Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_performance_test():
    """Run a simple performance test"""
    print("\n🔍 Running Performance Test...")
    
    start_time = time.time()
    
    # Make multiple requests to test performance
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/traffic_data")
            if response.status_code != 200:
                print(f"❌ Performance test failed at request {i+1}")
                return False
        except Exception as e:
            print(f"❌ Performance test error at request {i+1}: {str(e)}")
            return False
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 10
    
    print(f"✅ Performance Test: 10 requests in {total_time:.2f}s")
    print(f"   Average response time: {avg_time:.3f}s")
    
    return True

def main():
    """Main test function"""
    print("🚦 Smart Traffic Management System - Backend Test")
    print("=" * 60)
    print(f"Testing backend at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results
    tests = []
    
    # Run all tests
    tests.append(("Health Check", test_health_check()))
    tests.append(("Traffic Data", test_traffic_data()))
    tests.append(("Processing Status", test_processing_status()))
    tests.append(("Traffic Simulation", test_simulate_traffic()))
    tests.append(("Reset Signals", test_reset_signals()))
    tests.append(("Video Processing", test_video_processing()))
    tests.append(("Processed Frames", test_processed_frames()))
    tests.append(("Performance Test", run_performance_test()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend logs for issues.")
    
    # Success rate
    success_rate = (passed / total) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        exit(1)
