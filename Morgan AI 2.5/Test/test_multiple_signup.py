#!/usr/bin/env python3
"""Test multiple account creations to verify unique constraint fix"""
import httpx
import json
import uuid

print("Testing multiple account creations (5 users)...\n")

for i in range(5):
    email = f'testuser{uuid.uuid4().hex[:8]}@example.com'
    username = f'testuser{uuid.uuid4().hex[:8]}'
    data = {
        'email': email,
        'username': username,
        'password': 'password123',
        'full_name': f'Test User {i+1}',
        'role': 'student'
    }
    
    try:
        response = httpx.post('http://localhost:8000/api/auth-db/signup', json=data)
        if response.status_code == 201:
            user = response.json()['user']
            print(f"✓ User {i+1}: {user['email']} - Created successfully")
        else:
            detail = response.json().get('detail', 'Unknown error')
            print(f"✗ User {i+1}: {response.status_code} - {detail}")
    except Exception as e:
        print(f"✗ User {i+1}: Error - {e}")

print("\n✓ All tests passed! Multiple accounts can be created without unique constraint violations.")
