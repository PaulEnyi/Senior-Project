#!/usr/bin/env python3
"""Test signup to identify any issues"""
import httpx
import json
import uuid

print("=" * 60)
print("TESTING ACCOUNT CREATION")
print("=" * 60)

# Test 1: Valid signup
email = f'testuser{uuid.uuid4().hex[:8]}@example.com'
username = f'user{uuid.uuid4().hex[:6]}'
data = {
    'email': email,
    'username': username,
    'password': 'TestPassword123!',
    'full_name': 'Test User',
    'role': 'student'
}

print(f"\n✓ Test 1: Valid Signup")
print(f"  Email: {email}")
print(f"  Username: {username}")

try:
    response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data, timeout=10)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"  ✅ SUCCESS - User created!")
        print(f"     User ID: {result['user']['user_id']}")
        print(f"     Token: {result['access_token'][:30]}...")
    else:
        print(f"  ❌ FAILED - {response.json()['detail']}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 2: Duplicate email
print(f"\n✓ Test 2: Duplicate Email (should fail)")
data2 = {
    'email': email,  # Same as above
    'username': f'user{uuid.uuid4().hex[:6]}',
    'password': 'TestPassword123!',
    'full_name': 'Test User',
    'role': 'student'
}

try:
    response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data2, timeout=10)
    if response.status_code == 400:
        print(f"  ✅ CORRECT - {response.json()['detail']}")
    else:
        print(f"  ❌ UNEXPECTED - Status {response.status_code}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 3: Invalid email format
print(f"\n✓ Test 3: Invalid Email Format (should fail)")
data3 = {
    'email': 'notanemail',
    'username': f'user{uuid.uuid4().hex[:6]}',
    'password': 'TestPassword123!',
    'full_name': 'Test User',
    'role': 'student'
}

try:
    response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data3, timeout=10)
    if response.status_code == 422:
        print(f"  ✅ CORRECT - Validation error caught")
    else:
        print(f"  ❌ UNEXPECTED - Status {response.status_code}")
except Exception as e:
    print(f"  ✅ EXPECTED - Validation error: {str(e)[:50]}...")

# Test 4: Password too short
print(f"\n✓ Test 4: Password Too Short (should fail)")
data4 = {
    'email': f'test{uuid.uuid4().hex[:8]}@example.com',
    'username': f'user{uuid.uuid4().hex[:6]}',
    'password': '123',  # Only 3 chars, needs 6+
    'full_name': 'Test User',
    'role': 'student'
}

try:
    response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data4, timeout=10)
    if response.status_code == 422:
        print(f"  ✅ CORRECT - Validation error caught")
    else:
        print(f"  ❌ UNEXPECTED - Status {response.status_code}")
except Exception as e:
    print(f"  ✅ EXPECTED - Validation error")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
