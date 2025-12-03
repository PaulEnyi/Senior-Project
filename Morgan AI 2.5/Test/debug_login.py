#!/usr/bin/env python3
"""Debug login issue"""
import httpx
import json
import uuid

# Create test user
email = f'test{uuid.uuid4().hex[:8]}@example.com'
username = f'user{uuid.uuid4().hex[:6]}'

# Signup first
signup_data = {
    'email': email,
    'username': username,
    'password': 'TestPass123!',
    'full_name': 'Test User'
}

print(f"Creating user: {email}")
signup_response = httpx.post('http://localhost:8000/api/auth-db/signup', json=signup_data)
print(f"Signup response: {signup_response.status_code}")
if signup_response.status_code != 201:
    print(f"Error: {signup_response.json()}")
    exit(1)

# Now try login
login_data = {
    'email': email,
    'password': 'TestPass123!'
}

print(f"\nLogging in: {email}")
login_response = httpx.post('http://localhost:8000/api/auth-db/login', json=login_data)
print(f"Login response: {login_response.status_code}")
print(f"Response body: {json.dumps(login_response.json(), indent=2)}")
