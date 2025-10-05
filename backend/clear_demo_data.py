"""
Quick database seeding - clears existing demo data and recreates
"""
from database import get_supabase

print("🧹 Clearing demo data...")
supabase = get_supabase()

# Get institution ID
inst = supabase.table("institutions").select("id").eq("code", "BACE2023").execute()
if inst.data:
    inst_id = inst.data[0]['id']
    
    # Delete in order (due to foreign keys)
    print("   Deleting event participation...")
    supabase.table("event_participation").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting events...")
    supabase.table("events").delete().eq("institution_id", inst_id).execute()
    
    print("   Deleting book loans...")
    supabase.table("book_loans").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting library books...")
    supabase.table("library_books").delete().eq("institution_id", inst_id).execute()
    
    print("   Deleting fee transactions...")
    supabase.table("fee_transactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting fees...")
    supabase.table("fees").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting marks...")
    supabase.table("marks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting attendance...")
    supabase.table("attendance").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    print("   Deleting timetable...")
    supabase.table("timetable").delete().eq("institution_id", inst_id).execute()
    
    print("   Deleting subjects...")
    supabase.table("subjects").delete().eq("institution_id", inst_id).execute()
    
    print("   Deleting students...")
    supabase.table("students").delete().eq("institution_id", inst_id).execute()
    
    print("✅ Demo data cleared!")
else:
    print("ℹ️  No institution found, nothing to clear")

print("\n✅ Ready to run seed_database.py again")
