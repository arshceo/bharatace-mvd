import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, 'D:\\React Projects\\Bharatace_mvd\\backend')

from database import get_supabase
from auth import verify_password
from supabase import create_client

# Test login flow
email = "priya.sharma@bharatace.edu.in"
password = "password123"

print(f"🔍 Testing login for: {email}")
print(f"🔑 Password: {password}")
print()

# Get student from database using SERVICE ROLE KEY (bypasses RLS)
print("Using SERVICE ROLE KEY to bypass RLS...")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)
print("📡 Fetching student from database...")
student_response = supabase.table("students").select("*").eq("email", email).execute()

if not student_response.data:
    print("❌ Student not found!")
    sys.exit(1)

user = student_response.data[0]
print(f"✅ Found user: {user.get('full_name')} ({user.get('email')})")
print(f"   Roll Number: {user.get('roll_number')}")
print(f"   Has password_hash: {'Yes' if user.get('password_hash') else 'No'}")

if user.get('password_hash'):
    print(f"   Password hash (first 50 chars): {user['password_hash'][:50]}...")
    print()
    
    # Test password verification
    print(f"🔐 Verifying password...")
    is_valid = verify_password(password, user['password_hash'])
    
    if is_valid:
        print("✅ Password verification PASSED!")
        print("\n🎉 Login should work!")
    else:
        print("❌ Password verification FAILED!")
        print("\n⚠️  This is why login is failing!")
        
        # Try manual bcrypt check
        import bcrypt
        print("\n🔬 Manual bcrypt test:")
        try:
            manual_check = bcrypt.checkpw(
                password.encode('utf-8'),
                user['password_hash'].encode('utf-8')
            )
            print(f"   Manual check result: {manual_check}")
        except Exception as e:
            print(f"   Manual check error: {e}")
else:
    print("❌ No password_hash in database!")
