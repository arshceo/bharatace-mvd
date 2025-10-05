"""
Update database schema to support custom authentication
"""
from database import get_supabase

def update_schema():
    supabase = get_supabase()
    
    print("🔧 Updating database schema for custom authentication...")
    print("=" * 80)
    
    # Read the SQL file
    with open("schema_update.sql", "r") as f:
        sql = f.read()
    
    try:
        # Execute the SQL
        result = supabase.rpc("exec_sql", {"sql_query": sql}).execute()
        print("✅ Schema updated successfully!")
    except Exception as e:
        print(f"⚠️  Could not update via RPC: {e}")
        print("\n" + "=" * 80)
        print("📋 MANUAL STEPS REQUIRED:")
        print("=" * 80)
        print("\n1. Open your Supabase Dashboard: https://gdltegmlnhmfitsfkzcc.supabase.co")
        print("2. Go to: SQL Editor")
        print("3. Copy and paste the contents of 'schema_update.sql'")
        print("4. Click 'Run' to execute the SQL")
        print("\nOR run this SQL directly:")
        print("-" * 80)
        print(sql)
        print("-" * 80)

if __name__ == "__main__":
    update_schema()
