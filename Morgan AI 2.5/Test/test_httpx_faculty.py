#!/usr/bin/env python3
"""Test faculty extraction with httpx"""

import httpx
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"testfaculty{int(time.time())}@test.com"
TEST_USERNAME = f"testfacultyuser{int(time.time())}"
TEST_PASSWORD = "Test@123456"

def main():
    print(f"Testing faculty extraction")
    print("=" * 80)
    
    # Step 1: Signup
    print(f"\n1. Signup: {TEST_EMAIL} / {TEST_USERNAME}")
    signup_resp = httpx.post(
        f"{BASE_URL}/api/auth/signup",
        json={
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        },
        timeout=10
    )
    print(f"   Status: {signup_resp.status_code}")
    if signup_resp.status_code != 201:
        print(f"   Error: {signup_resp.text[:500]}")
        return
    
    print(f"   ✓ User created")
    
    # Step 2: Login
    print(f"\n2. Login")
    login_resp = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=10
    )
    print(f"   Status: {login_resp.status_code}")
    if login_resp.status_code != 200:
        print(f"   Error: {login_resp.text[:200]}")
        return
    
    token = login_resp.json()["access_token"]
    print(f"   ✓ Logged in, token: {token[:30]}...")
    
    # Step 3: Send chat message
    print(f"\n3. Sending faculty query (this may take 30+ seconds for Playwright rendering)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    chat_resp = httpx.post(
        f"{BASE_URL}/api/chat/message",
        json={
            "message": "Who are the faculty members in Computer Science?",
            "thread_id": None
        },
        headers=headers,
        timeout=180  # 3 minutes for Playwright rendering
    )
    
    print(f"   Status: {chat_resp.status_code}")
    if chat_resp.status_code != 200:
        print(f"   Error: {chat_resp.text[:500]}")
        return
    
    # Step 4: Analyze response
    response_data = chat_resp.json()
    response_text = response_data.get("message", "")
    
    print(f"\n4. Response Analysis:")
    print(f"   Length: {len(response_text)} chars")
    print(f"\n   Content preview (first 600 chars):")
    print(f"   {'-' * 70}")
    print(f"   {response_text[:600]}")
    print(f"   {'-' * 70}")
    
    # Check for faculty indicators
    indicators = {
        "Dr.": "Found Dr. title",
        "Professor": "Found Professor title",
        "Wang": "Found faculty member name",
        "adviser": "Found adviser reference",
        "office": "Found office reference",
        "Morgan State": "Found institution name",
        "contact": "Found contact info"
    }
    
    print(f"\n5. Faculty Indicators Found:")
    found_any = False
    for indicator, description in indicators.items():
        if indicator in response_text:
            print(f"   ✓ {description}")
            found_any = True
    
    if not found_any:
        print(f"   ✗ No faculty indicators found")
        print(f"\n   This may indicate:")
        print(f"   - Playwright extraction not working")
        print(f"   - Faculty content not present on rendered page")
        print(f"   - BeautifulSoup patterns not matching content")

if __name__ == "__main__":
    main()
