#!/usr/bin/env python3
"""Test account creation fix for student_id unique constraint"""
import httpx
import json
import uuid

email = f'testuser{uuid.uuid4().hex[:8]}@example.com'
username = f'testuser{uuid.uuid4().hex[:8]}'
data = {
    'email': email,
    'username': username,
    'password': 'password123',
    'full_name': 'Test User New',
    'role': 'student'
}

print(f"Testing signup with email: {email}")
print(f"Username: {username}")

try:
    response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data)
    print(f'\nStatus Code: {response.status_code}')
    
    result = response.json()
    if response.status_code == 201:
        print('\n✓ SUCCESS! Account created successfully!')
        token = result['access_token'][:30]
        print(f'Access Token: {token}...')
        print(f'User ID: {result["user"]["user_id"]}')
        print(f'Email: {result["user"]["email"]}')
        print(f'Username: {result["user"]["username"]}')
        print(f'Role: {result["user"]["role"]}')
    else:
        print(f'\n✗ FAILED!')
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
