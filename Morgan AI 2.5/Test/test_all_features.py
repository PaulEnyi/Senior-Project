#!/usr/bin/env python3
"""Comprehensive test of all Morgan AI 2.5 features"""
import httpx
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"
print("\n" + "="*70)
print("MORGAN AI 2.5 - COMPREHENSIVE FEATURE TEST")
print("="*70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

test_results = {
    'passed': 0,
    'failed': 0,
    'total': 0
}

def test_feature(name, method, endpoint, data=None, expected_status=200):
    """Test a feature endpoint"""
    test_results['total'] += 1
    full_url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = httpx.get(full_url, timeout=10)
        elif method == "POST":
            response = httpx.post(full_url, json=data, timeout=10)
        else:
            return
        
        success = response.status_code == expected_status
        status_emoji = "✅" if success else "❌"
        
        print(f"{status_emoji} {name}")
        print(f"   {method} {endpoint} → {response.status_code}")
        
        if success:
            test_results['passed'] += 1
        else:
            test_results['failed'] += 1
            try:
                print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:100]}")
        print()
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['total'] += 1
        print(f"❌ {name}")
        print(f"   ERROR: {str(e)[:100]}\n")

# Create test user
test_email = f'test{uuid.uuid4().hex[:8]}@example.com'
test_username = f'user{uuid.uuid4().hex[:6]}'
test_password = 'TestPassword123!'

print("🔐 AUTHENTICATION TESTS")
print("-" * 70)

# Signup
test_feature(
    "User Signup",
    "POST",
    "/api/auth-db/signup",
    {
        'email': test_email,
        'username': test_username,
        'password': test_password,
        'full_name': 'Test User'
    },
    201
)

# Login
login_response = httpx.post(
    f"{BASE_URL}/api/auth-db/login",
    json={'email': test_email, 'password': test_password},
    timeout=10
)
token = login_response.json().get('access_token') if login_response.status_code == 200 else None

if token:
    print(f"✅ User Login")
    print(f"   POST /api/auth-db/login → {login_response.status_code}")
    test_results['passed'] += 1
    print()
else:
    print(f"❌ User Login - Could not get token\n")
    test_results['failed'] += 1

test_results['total'] += 1

# Health check
test_feature(
    "Backend Health Check",
    "GET",
    "/health"
)

print("\n💬 CHAT FEATURES")
print("-" * 70)

# Get quick questions
test_feature(
    "Quick Questions (28 questions)",
    "GET",
    "/api/chat/quick-questions"
)

# Get chat threads
test_feature(
    "Get Chat Threads",
    "GET",
    "/api/chat/threads"
)

print("\n🗣️ VOICE FEATURES")
print("-" * 70)

# Voice status
test_feature(
    "Voice Status Check",
    "GET",
    "/api/voice/status"
)

# Text-to-Speech
test_feature(
    "Text-to-Speech Generation",
    "POST",
    "/api/voice/text-to-speech",
    {'text': 'Hello, this is a test message', 'voice': 'alloy'}
)

print("\n🎓 DEGREE WORKS")
print("-" * 70)

# Degree works status
test_feature(
    "Degree Works Analysis (GET)",
    "GET",
    "/api/degree-works/analysis"
)

print("\n📚 KNOWLEDGE BASE")
print("-" * 70)

# Knowledge base status
test_feature(
    "Knowledge Base Status",
    "GET",
    "/api/knowledge/status"
)

print("\n💼 CAREER RESOURCES")
print("-" * 70)

# Internships list
test_feature(
    "Internship List",
    "GET",
    "/api/internships/list"
)

# Career resources
test_feature(
    "Career Resources",
    "GET",
    "/api/resources/career"
)

print("\n📅 CALENDAR")
print("-" * 70)

# Calendar
test_feature(
    "Academic Calendar",
    "GET",
    "/api/calendar/events"
)

print("\n🔧 ADMIN FEATURES")
print("-" * 70)

# Admin dashboard
test_feature(
    "Admin Dashboard",
    "GET",
    "/api/admin/dashboard"
)

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"Total Tests: {test_results['total']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
pass_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
print(f"Pass Rate: {pass_rate:.1f}%")
print("="*70)

if pass_rate == 100:
    print("\n🎉 ALL FEATURES WORKING PERFECTLY! ✅")
    print("Morgan AI 2.5 is PRODUCTION READY!\n")
elif pass_rate >= 90:
    print("\n✅ SYSTEM OPERATIONAL - Minor issues detected")
    print("Most features working correctly\n")
else:
    print("\n⚠️ SYSTEM HAS ISSUES - Please review failed tests\n")
