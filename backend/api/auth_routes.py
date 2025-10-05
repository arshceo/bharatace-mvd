"""
Authentication Routes
Handles user signup, login, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import uuid
import logging
from typing import Optional
from supabase import create_client
import os

from models import LoginRequest, SignupRequest, TokenResponse
from database import get_supabase
from auth import hash_password, verify_password, create_access_token
from settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def get_supabase_admin():
    """Get Supabase client with admin (service role) access to bypass RLS for authentication"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new student account.
    
    Creates:
    1. User account in Supabase Auth
    2. Student profile in students table
    
    Returns JWT token for immediate login.
    """
    try:
        # Use admin client to bypass RLS for auth operations
        supabase = get_supabase_admin()
        
        # Check if email already exists
        existing_user = supabase.table("students")\
            .select("email")\
            .eq("email", request.email)\
            .execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if roll number already exists
        existing_roll = supabase.table("students")\
            .select("roll_number")\
            .eq("roll_number", request.roll_number)\
            .execute()
        
        if existing_roll.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roll number already registered"
            )
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Get or create default institution (for MVP, using single institution)
        institution_response = supabase.table("institutions")\
            .select("*")\
            .limit(1)\
            .execute()
        
        if not institution_response.data:
            # Create default institution
            institution_id = str(uuid.uuid4())
            institution_data = {
                "id": institution_id,
                "name": "BharatAce College",
                "code": "BAC001",
                "address": "Sample Address",
                "contact_email": "admin@bharatace.edu",
                "contact_phone": "+91 1234567890"
            }
            supabase.table("institutions").insert(institution_data).execute()
        else:
            institution_id = institution_response.data[0]['id']
        
        # Create student record
        student_id = str(uuid.uuid4())
        student_data = {
            "id": student_id,
            "institution_id": institution_id,
            "roll_number": request.roll_number,
            "full_name": request.full_name,
            "email": request.email,
            "phone": request.phone,
            "semester": request.semester,
            "department": request.department,
            "admission_year": datetime.now().year,
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        
        student_response = supabase.table("students").insert(student_data).execute()
        
        if not student_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create student account"
            )
        
        student = student_response.data[0]
        
        # Create JWT token
        token_data = {
            "sub": student['id'],
            "email": student['email'],
            "role": "student"
        }
        access_token = create_access_token(token_data)
        
        # Prepare user data for frontend
        user_data = {
            "id": student['id'],
            "email": student['email'],
            "role": "student",
            "student_data": {
                "id": student['id'],
                "roll_number": student['roll_number'],
                "full_name": student['full_name'],
                "semester": student['semester'],
                "department": student['department'],
                "cgpa": student.get('cgpa')
            }
        }
        
        logger.info(f"New student registered: {student['email']}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Supports both students and admins.
    """
    try:
        # Use admin client to bypass RLS for auth operations
        supabase = get_supabase_admin()
        
        # Try to find student first
        student_response = supabase.table("students")\
            .select("*")\
            .eq("email", request.email)\
            .execute()
        
        if student_response.data:
            user = student_response.data[0]
            user_type = "student"
        else:
            # Try admin users
            admin_response = supabase.table("admin_users")\
                .select("*")\
                .eq("email", request.email)\
                .execute()
            
            if admin_response.data:
                user = admin_response.data[0]
                user_type = "admin"
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
        
        # Verify password
        if not verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT token
        token_data = {
            "sub": user['id'],
            "email": user['email'],
            "role": user_type
        }
        access_token = create_access_token(token_data)
        
        # Prepare user data for frontend
        user_data = {
            "id": user['id'],
            "email": user['email'],
            "role": user_type
        }
        
        if user_type == "student":
            user_data["student_data"] = {
                "id": user['id'],
                "roll_number": user['roll_number'],
                "full_name": user['full_name'],
                "semester": user['semester'],
                "department": user['department'],
                "cgpa": user.get('cgpa')
            }
        else:
            user_data["admin_data"] = {
                "id": user['id'],
                "full_name": user['full_name'],
                "role": user.get('role', 'admin')
            }
        
        logger.info(f"User logged in: {user['email']} ({user_type})")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(current_token: str):
    """
    Refresh an expired or expiring JWT token.
    
    Note: In production, implement proper refresh token rotation.
    """
    try:
        # Decode the existing token (even if expired)
        from jose import jwt, JWTError
        
        try:
            payload = jwt.decode(
                current_token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration for refresh
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new token with same data
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Create new access token
        token_data = {
            "sub": user_id,
            "email": email,
            "role": role
        }
        new_access_token = create_access_token(token_data)
        
        logger.info(f"Token refreshed for user: {email}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.get("/me")
async def get_current_user_profile(user_id: str):
    """
    Get current user's profile data.
    
    Used to verify token and fetch latest user info.
    """
    try:
        supabase = get_supabase()
        
        # Try to find student
        student_response = supabase.table("students")\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if student_response.data:
            user = student_response.data[0]
            return {
                "id": user['id'],
                "email": user['email'],
                "role": "student",
                "student_data": {
                    "id": user['id'],
                    "roll_number": user['roll_number'],
                    "full_name": user['full_name'],
                    "semester": user['semester'],
                    "department": user['department'],
                    "cgpa": user.get('cgpa'),
                    "phone": user.get('phone')
                }
            }
        
        # Try admin
        admin_response = supabase.table("admin_users")\
            .select("*")\
            .eq("id", user_id)\
            .execute()
        
        if admin_response.data:
            user = admin_response.data[0]
            return {
                "id": user['id'],
                "email": user['email'],
                "role": "admin",
                "admin_data": {
                    "id": user['id'],
                    "full_name": user['full_name'],
                    "role": user.get('role', 'admin')
                }
            }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )
