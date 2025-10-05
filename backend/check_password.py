import os
from dotenv import load_dotenv
from supabase import create_client
import bcrypt

# Load environment variables
load_dotenv()

# Create Supabase client with service role key
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Check Priya's account
print("🔍 Checking Priya's account...")
result = supabase.table("students").select("email, password_hash, roll_number, full_name").eq("email", "priya.sharma@bharatace.edu.in").execute()

if result.data:
    student = result.data[0]
    print(f"\n✅ Found student: {student['full_name']} ({student['email']})")
    print(f"Roll Number: {student['roll_number']}")
    
    if student.get('password_hash'):
        print(f"Password hash exists: {student['password_hash'][:30]}...")
        
        # Test password verification
        test_password = "password123"
        print(f"\n🔐 Testing password: '{test_password}'")
        
        try:
            is_valid = bcrypt.checkpw(
                test_password.encode('utf-8'),
                student['password_hash'].encode('utf-8')
            )
            print(f"✅ Password verification: {is_valid}")
        except Exception as e:
            print(f"❌ Error verifying password: {e}")
    else:
        print("❌ No password_hash found!")
else:
    print("❌ Student not found!")

# Check all students
print("\n\n📋 Checking all students with passwords...")
all_students = supabase.table("students").select("email, password_hash, roll_number, full_name").execute()

for student in all_students.data:
    has_password = "✅" if student.get('password_hash') else "❌"
    print(f"{has_password} {student.get('email', 'N/A')} - {student.get('full_name', 'N/A')}")
