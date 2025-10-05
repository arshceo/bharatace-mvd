import requests
import json

# Login
print("\n" + "="*60)
print("TESTING SUPER SMART AGENT")
print("="*60 + "\n")

print("Step 1: Logging in...")
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "email": "sneha.patel@bharatace.edu.in",
        "password": "password123"
    }
)

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data["access_token"]
    student = login_data["user"]["student_data"]
    print(f"✓ Login successful!")
    print(f"  Student: {student['full_name']}")
    print(f"  CGPA (from login): {student['cgpa']}")
else:
    print(f"✗ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

# Ask for CGPA
print("\nStep 2: Asking AI Agent for CGPA...")
ask_response = requests.post(
    "http://localhost:8000/ask",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "What is my current CGPA?"}
)

if ask_response.status_code == 200:
    answer = ask_response.json()["answer"]
    print("\n" + "="*60)
    print("AGENT RESPONSE:")
    print("="*60)
    print(answer)
    print("="*60 + "\n")
else:
    print(f"✗ Query failed: {ask_response.status_code}")
    print(ask_response.text)
