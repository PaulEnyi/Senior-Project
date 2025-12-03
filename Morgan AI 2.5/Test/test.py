import requests
import json
import time
import uuid

# Create unique user
unique_id = str(uuid.uuid4())[:8]
email = f"test{unique_id}@test.com"
username = f"testuser{unique_id}"

# First, signup a new user if needed
signup_data = {"email": email, "username": username, "password": "test123", "full_name": "Test User"}
signup_resp = requests.post("http://localhost:8000/api/auth/signup", json=signup_data)
print(f"Signup status: {signup_resp.status_code}")
if signup_resp.status_code == 201:
    print("User created successfully")
elif "already" in signup_resp.text.lower():
    print("User already exists (that's ok)")
else:
    print(f"Signup error: {signup_resp.text[:200]}")

# Now login
login_data = {"email": email, "password": "test123"}
login_resp = requests.post("http://localhost:8000/api/auth/login", json=login_data)
print(f"Login status: {login_resp.status_code}")
if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    print(f"Got token: {token[:30]}..." if token else f"No token in response")
    
    if token:
        # Send chat message
        headers = {"Authorization": f"Bearer {token}"}
        chat_data = {"message": "Who are the faculty members in Computer Science?"}
        print("\nSending faculty query to test Playwright web search...")
        start = time.time()
        chat_resp = requests.post("http://localhost:8000/api/chat/message", json=chat_data, headers=headers, timeout=90)
        elapsed = time.time() - start
        print(f"Chat status: {chat_resp.status_code}, took {elapsed:.1f}s")
        if chat_resp.status_code == 200:
            resp_json = chat_resp.json()
            content = resp_json.get("content", "")
            print(f"\nResponse length: {len(content)} chars")
            print(f"\n=== AI Response (first 1000 chars) ===")
            print(content[:1000])
            
            # Check if Playwright found faculty info
            if any(name in content.lower() for name in ["frank batten", "tsikata", "paul natesan", "azriel", "ying liu", "malay patel", "faculty", "director", "dr."]):
                print("\n✅ SUCCESS: Faculty information found in response!")
            else:
                print("\n⚠️ No specific faculty names detected in response")
        else:
            print(f"Error: {chat_resp.text[:500]}")
else:
    print(f"Login error: {login_resp.text}")



