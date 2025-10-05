"""Check actual database schema"""
from database import get_supabase

supabase = get_supabase()

# Check institutions table
print("Checking institutions table...")
try:
    result = supabase.table("institutions").select("*").limit(1).execute()
    print(f"✓ Institutions table exists, columns: {result.data}")
except Exception as e:
    print(f"✗ Error: {e}")

# Check students table
print("\nChecking students table...")
try:
    result = supabase.table("students").select("*").limit(1).execute()
    if result.data:
        print(f"✓ Students table exists, sample: {result.data[0].keys()}")
    else:
        print("✓ Students table exists but is empty")
except Exception as e:
    print(f"✗ Error: {e}")

# Check subjects table
print("\nChecking subjects table...")
try:
    result = supabase.table("subjects").select("*").limit(1).execute()
    if result.data:
        print(f"✓ Subjects table exists, sample: {result.data[0].keys()}")
    else:
        print("✓ Subjects table exists but is empty")
except Exception as e:
    print(f"✗ Error: {e}")
