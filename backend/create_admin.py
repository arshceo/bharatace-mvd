"""
Create Admin User for CMS
Run this script to create a super admin account
"""

import bcrypt
from database import get_supabase_admin
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_admin():
    """Create super admin user"""
    supabase = get_supabase_admin()
    
    # Admin credentials
    admin_email = "admin@bharatace.com"
    admin_password = "Admin@123456"
    admin_name = "Super Admin"
    
    # Check if admin already exists
    existing = supabase.table("admin_users").select("id").eq("email", admin_email).execute()
    
    if existing.data:
        print(f"❌ Admin with email {admin_email} already exists!")
        print(f"✅ You can login with:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        return
    
    # Hash password
    password_hash = hash_password(admin_password)
    
    # Default super admin permissions (all enabled)
    permissions = {
        "can_manage_institutions": True,
        "can_manage_students": True,
        "can_manage_faculty": True,
        "can_enter_marks": True,
        "can_mark_attendance": True,
        "can_manage_fees": True,
        "can_manage_library": True,
        "can_manage_events": True,
        "can_manage_knowledge_base": True,
        "can_view_reports": True,
        "can_export_data": True,
        "can_delete_records": True
    }
    
    # Create admin user
    admin_data = {
        "email": admin_email,
        "password_hash": password_hash,
        "full_name": admin_name,
        "role": "super_admin",
        "institution_id": None,
        "permissions": permissions,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        result = supabase.table("admin_users").insert(admin_data).execute()
        
        if result.data:
            print("✅ Super Admin created successfully!")
            print("\n" + "="*50)
            print("🔐 ADMIN LOGIN CREDENTIALS")
            print("="*50)
            print(f"Email:    {admin_email}")
            print(f"Password: {admin_password}")
            print("="*50)
            print("\n📍 Login at: http://localhost:3001")
            print("✨ Role: Super Admin (Full Access)")
        else:
            print("❌ Failed to create admin user")
            
    except Exception as e:
        print(f"❌ Error creating admin: {str(e)}")

if __name__ == "__main__":
    create_admin()
