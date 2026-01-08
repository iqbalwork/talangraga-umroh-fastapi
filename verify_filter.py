import urllib.request
import urllib.parse
import json
import ssl

API_URL = "http://localhost:8000"

def login(email, password):
    url = f"{API_URL}/auth/login"
    data = json.dumps({"identifier": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode())
                return result["data"]["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def test_transactions(token, user_id=None, periode_id=None):
    url = f"{API_URL}/transactions/"
    params = {}
    if user_id:
        params["user_id"] = user_id
    if periode_id:
        params["periode_id"] = periode_id
    
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.status}")
            print(f"Response: {response.read().decode()}")
    except Exception as e:
        print(f"Request failed: {e}")

def register(email, password):
    url = f"{API_URL}/auth/register"
    # Using multipart/form-data is complex with urllib standard library without boundaries manually.
    # But the API expects Form(...) which is application/x-www-form-urlencoded or multipart/form-data.
    # Let's try x-www-form-urlencoded first as it is easier.
    data = urllib.parse.urlencode({
        "fullname": "Test Admin",
        "username": "testadmin_" + email.split("@")[0],
        "email": email,
        "password": password,
        "user_type": "admin"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    # req.add_header("Content-Type", "application/x-www-form-urlencoded") # urllib allows this by default for urlencoded data? No, default is application/x-www-form-urlencoded
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Registration successful")
                return True
    except Exception as e:
        print(f"Registration failed: {e}")
        # If already registered, still try to login
        if "Email already registered" in str(e) or "HTTP Error 400" in str(e):
             print("User might already exist, proceeding to login...")
             return True
    return False

if __name__ == "__main__":
    admin_email = "temp_admin_test@talangraga.com" 
    admin_password = "password123"
    
    # Register first
    print("Registering temporary admin user...")
    register(admin_email, admin_password)
    
    print("Logging in as admin...")
    token = login(admin_email, admin_password)
    
    # You might need to change this ID to a valid user ID in your DB
    target_user_id = 1 
    
    if token:
        print(f"Login successful, token: {token[:10]}...")
        print("\nTesting retrieval of transactions for specific user...")
        test_transactions(token, user_id=target_user_id)
        
        print("\nTesting retrieval of transactions for specific user and periode...")
        test_transactions(token, user_id=target_user_id, periode_id=1)
