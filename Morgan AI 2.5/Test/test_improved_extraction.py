#!/usr/bin/env python3
"""Test the improved web search extraction end-to-end"""

import json
import httpx
import time

BASE_URL = "http://localhost:8000"

def signup_user():
    """Create a test user"""
    resp = httpx.post(f"{BASE_URL}/api/auth/signup", json={
        "email": f"test{int(time.time())}@test.com",
        "password": "Test@123456"
    })
    print(f"Signup: {resp.status_code}")
    if resp.status_code == 201:
        return resp.json()["user"]["email"]
    return None

def login_user(email):
    """Login and get token"""
    resp = httpx.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": "Test@123456"
    })
    print(f"Login: {resp.status_code}")
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        return token
    return None

def send_chat_message(token, message):
    """Send a chat message"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = httpx.post(
        f"{BASE_URL}/api/chat/message",
        json={"message": message, "thread_id": None},
        headers=headers
    )
    print(f"Chat message: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nAssistant Response:")
        print(data["response"]["content"][:1000])
        print(f"\n[Length: {len(data['response']['content'])} chars]")
        # Check if faculty names are in the response
        faculty_names = ["Wang", "Dr. ", "Professor", "adviser", "office hours"]
        for name in faculty_names:
            if name.lower() in data["response"]["content"].lower():
                print(f"✓ Found '{name}' in response")
    return resp.json() if resp.status_code == 200 else None

if __name__ == "__main__":
    print("=" * 80)
    print("Testing improved web search extraction")
    print("=" * 80)
    
    email = signup_user()
    if not email:
        print("Signup failed")
        exit(1)
    
    token = login_user(email)
    if not token:
        print("Login failed")
        exit(1)
    
    print("\nSending faculty query...")
    send_chat_message(token, "Who are the faculty members in Computer Science?")
    
    print("\n" + "=" * 80)
    print("Test complete")
    print("=" * 80)
