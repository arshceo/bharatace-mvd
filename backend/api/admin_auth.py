"""
Admin Authentication API
Handles admin login, registration, and permission management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
import bcrypt
import jwt
from datetime import datetime, timedelta
from database import get_supabase_admin
from admin_models.admin import (
    AdminCreate, AdminLogin, AdminResponse, AdminToken,
    AdminUpdate, AdminRole, AdminPermissions
)
from settings import settings

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_admin_token(admin_id: str, email: str, role: str) -> str:
    """Create JWT token for admin"""
    payload = {
        "admin_id": admin_id,
        "email": email,
        "role": role,
        "type": "admin",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")


async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
        
        if payload.get("type") != "admin":
            raise HTTPException(status_code=401, detail="Invalid admin token")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def check_permission(
    permission: str,
    admin_data: Dict = Depends(verify_admin_token)
) -> Dict:
    """Check if admin has specific permission"""
    supabase = get_supabase_admin()
    
    # Fetch admin permissions
    admin = supabase.table("admin_users").select("*").eq("id", admin_data["admin_id"]).execute()
    
    if not admin.data:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    admin_info = admin.data[0]
    
    # Super admin has all permissions
    if admin_info["role"] == "super_admin":
        return admin_info
    
    # Check specific permission
    permissions = admin_info.get("permissions", {})
    if not permissions.get(permission, False):
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied: {permission}"
        )
    
    return admin_info


@router.post("/register", response_model=AdminResponse)
async def register_admin(admin_data: AdminCreate):
    """
    Register new admin user
    Only super_admin can create other admins
    """
    supabase = get_supabase_admin()
    
    try:
        # Check if email exists
        existing = supabase.table("admin_users").select("id").eq("email", admin_data.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Set default permissions based on role
        if not admin_data.permissions:
            if admin_data.role == AdminRole.SUPER_ADMIN:
                permissions = AdminPermissions(
                    can_manage_institutions=True,
                    can_manage_students=True,
                    can_manage_faculty=True,
                    can_enter_marks=True,
                    can_mark_attendance=True,
                    can_manage_fees=True,
                    can_manage_library=True,
                    can_manage_events=True,
                    can_manage_knowledge_base=True,
                    can_view_reports=True,
                    can_export_data=True,
                    can_delete_records=True
                ).dict()
            elif admin_data.role == AdminRole.INSTITUTION_ADMIN:
                permissions = AdminPermissions(
                    can_manage_students=True,
                    can_manage_faculty=True,
                    can_enter_marks=True,
                    can_mark_attendance=True,
                    can_manage_fees=True,
                    can_manage_library=True,
                    can_manage_events=True,
                    can_manage_knowledge_base=True,
                    can_view_reports=True,
                    can_export_data=True
                ).dict()
            elif admin_data.role == AdminRole.FACULTY:
                permissions = AdminPermissions(
                    can_enter_marks=True,
                    can_mark_attendance=True,
                    can_view_reports=True
                ).dict()
            else:
                permissions = AdminPermissions().dict()
        else:
            permissions = admin_data.permissions
        
        # Hash password
        password_hash = hash_password(admin_data.password)
        
        # Create admin
        result = supabase.table("admin_users").insert({
            "email": admin_data.email,
            "password_hash": password_hash,
            "full_name": admin_data.full_name,
            "role": admin_data.role.value,
            "institution_id": admin_data.institution_id,
            "permissions": permissions
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create admin")
        
        return AdminResponse(**result.data[0])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=AdminToken)
async def admin_login(credentials: AdminLogin):
    """
    Admin login
    Returns JWT token with admin permissions
    """
    supabase = get_supabase_admin()
    
    try:
        # Find admin by email
        admin = supabase.table("admin_users").select("*").eq("email", credentials.email).execute()
        
        if not admin.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        admin_data = admin.data[0]
        
        # Check if admin is active
        if not admin_data.get("is_active", True):
            raise HTTPException(status_code=403, detail="Account is deactivated")
        
        # Verify password
        if not verify_password(credentials.password, admin_data["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate token
        token = create_admin_token(
            admin_data["id"],
            admin_data["email"],
            admin_data["role"]
        )
        
        # Remove password hash from response
        admin_data.pop("password_hash")
        
        return AdminToken(
            access_token=token,
            admin=AdminResponse(**admin_data)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=AdminResponse)
async def get_current_admin(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get current admin user info
    """
    supabase = get_supabase_admin()
    
    admin = supabase.table("admin_users").select("*").eq("id", admin_data["admin_id"]).execute()
    
    if not admin.data:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    admin_info = admin.data[0]
    admin_info.pop("password_hash", None)
    
    return AdminResponse(**admin_info)


@router.patch("/me", response_model=AdminResponse)
async def update_admin_profile(
    update_data: AdminUpdate,
    admin_data: Dict = Depends(verify_admin_token)
):
    """
    Update admin profile
    """
    supabase = get_supabase_admin()
    
    # Build update object
    updates = {}
    if update_data.full_name is not None:
        updates["full_name"] = update_data.full_name
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updates["updated_at"] = datetime.utcnow().isoformat()
    
    # Update admin
    result = supabase.table("admin_users").update(updates).eq("id", admin_data["admin_id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    
    admin_info = result.data[0]
    admin_info.pop("password_hash", None)
    
    return AdminResponse(**admin_info)


@router.get("/permissions")
async def get_admin_permissions(admin_data: Dict = Depends(verify_admin_token)) -> Dict:
    """
    Get current admin permissions
    """
    supabase = get_supabase_admin()
    
    admin = supabase.table("admin_users").select("role, permissions").eq("id", admin_data["admin_id"]).execute()
    
    if not admin.data:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "role": admin.data[0]["role"],
        "permissions": admin.data[0]["permissions"]
    }
