#!/usr/bin/env python3
"""Test improved faculty extraction with actual chat"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"testfaculty{int(time.time())}@test.com"
TEST_PASSWORD = "Test@123456"

def test_with_curl():
    """Use curl-like commands to test"""
    import subprocess
    
    # Signup
    signup_cmd = f"""
    curl -X POST {BASE_URL}/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{{"email": "{TEST_EMAIL}", "password": "{TEST_PASSWORD}"}}'
    """
    print(f"Signup: {TEST_EMAIL}")
    result = subprocess.run(signup_cmd, shell=True, capture_output=True, text=True)
    if "201" not in result.stdout:
        print(f"Error: {result.stdout[:200]}")
        return
    
    signup_resp = json.loads(result.stdout)
    print(f"✓ Signup successful")
    
    # Login
    login_cmd = f"""
    curl -X POST {BASE_URL}/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{{"email": "{TEST_EMAIL}", "password": "{TEST_PASSWORD}"}}'
    """
    result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
    login_resp = json.loads(result.stdout)
    token = login_resp.get("access_token")
    print(f"✓ Login successful")
    
    # Send chat message
    chat_cmd = f"""
    curl -X POST {BASE_URL}/api/chat/message \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{{"message": "Who are the faculty members in Computer Science?", "thread_id": null}}'
    """
    print(f"\nSending faculty query...")
    result = subprocess.run(chat_cmd, shell=True, capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    
    try:
        chat_resp = json.loads(result.stdout)
        response_text = chat_resp.get("response", {}).get("content", "")
        
        print(f"\nAssistant Response ({len(response_text)} chars):")
        print(response_text[:800])
        
        # Check for faculty indicators
        indicators = ["Dr.", "Professor", "Wang", "adviser", "office", "contact"]
        found = [ind for ind in indicators if ind in response_text]
        
        if found:
            print(f"\n✓ Faculty indicators found: {', '.join(found)}")
        else:
            print(f"\n✗ No faculty indicators found in response")
            
    except json.JSONDecodeError:
        print(f"Failed to parse response: {result.stdout[:500]}")

if __name__ == "__main__":
    test_with_curl()
