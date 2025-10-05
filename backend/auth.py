"""
Authentication and Authorization Module
Handles JWT verification, user authentication, and role-based access control.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
from datetime import datetime
import logging

from settings import settings
from database import get_supabase

logger = logging.getLogger(__name__)

# Security scheme for FastAPI
security = HTTPBearer()


class AuthUser:
    """Represents an authenticated user with their data"""
    
    def __init__(self, user_id: str, email: str, role: str = "student", student_data: Optional[Dict] = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.student_data = student_data or {}
    
    @property
    def student_id(self) -> Optional[str]:
        """Get the student's database ID"""
        return self.student_data.get('id')
    
    @property
    def roll_number(self) -> Optional[str]:
        """Get the student's roll number"""
        return self.student_data.get('student_id')
    
    @property
    def full_name(self) -> str:
        """Get the student's full name"""
        first_name = self.student_data.get('first_name', '')
        last_name = self.student_data.get('last_name', '')
        return f"{first_name} {last_name}".strip() or self.email


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify a Supabase JWT token.
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode the JWT token
        # Supabase uses the JWT_SECRET from your project settings
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Check if token is expired
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        logger.info(f"Token verified for user: {payload.get('sub')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    Dependency to get the current authenticated user.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token with Supabase
    3. Fetches the user's profile from the database
    4. Returns an AuthUser object
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: AuthUser = Depends(get_current_user)):
            return {"user_id": user.user_id, "email": user.email}
    """
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify token
        payload = verify_jwt_token(token)
        
        # Extract user ID from token
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        # Fetch student profile from database using service role to bypass RLS
        from supabase import create_client
        from settings import settings
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # Query by id (which is the UUID we stored in JWT sub claim)
        response = supabase.table("students").select("*").eq("id", user_id).execute()
        
        student_data = {}
        role = "student"
        
        if response.data and len(response.data) > 0:
            student_data = response.data[0]
            logger.info(f"Student profile loaded: {student_data.get('roll_number')}")
        else:
            # Check if user is an admin (query by id)
            admin_response = supabase.table("admin_users").select("*").eq("id", user_id).execute()
            if admin_response.data and len(admin_response.data) > 0:
                role = admin_response.data[0].get('role', 'admin')
                logger.info(f"Admin user logged in: {email}")
            else:
                logger.warning(f"No profile found for user: {user_id}")
        
        return AuthUser(
            user_id=user_id,
            email=email,
            role=role,
            student_data=student_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_student(
    user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """
    Dependency to get the current authenticated student.
    Ensures the user has a student profile.
    
    Usage:
        @app.get("/student-only")
        async def student_route(student: AuthUser = Depends(get_current_student)):
            return {"student_id": student.student_id}
    """
    if not user.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a student profile",
        )
    
    return user


async def get_current_admin(
    user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """
    Dependency to get the current authenticated admin.
    Ensures the user has admin privileges.
    
    Usage:
        @app.get("/admin-only")
        async def admin_route(admin: AuthUser = Depends(get_current_admin)):
            return {"admin_email": admin.email}
    """
    if user.role not in ['admin', 'super_admin', 'faculty', 'staff']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return user


async def verify_admin_token(token: str) -> bool:
    """
    Verify if a token belongs to an admin user.
    Used for CMS authentication.
    
    Args:
        token: JWT token string
        
    Returns:
        True if user is admin, False otherwise
    """
    try:
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")
        
        supabase = get_supabase()
        response = supabase.table("admin_users").select("*").eq("user_id", user_id).execute()
        
        return response.data and len(response.data) > 0
        
    except Exception as e:
        logger.error(f"Error verifying admin token: {str(e)}")
        return False


class OptionalAuth:
    """
    Optional authentication dependency.
    Returns AuthUser if token is valid, None otherwise.
    Useful for endpoints that work both with and without authentication.
    
    Usage:
        @app.get("/public-or-personalized")
        async def flexible_route(user: Optional[AuthUser] = Depends(OptionalAuth())):
            if user:
                return {"message": f"Hello {user.full_name}!"}
            return {"message": "Hello guest!"}
    """
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[AuthUser]:
        if not credentials:
            return None
        
        try:
            token = credentials.credentials
            payload = verify_jwt_token(token)
            user_id = payload.get("sub")
            email = payload.get("email")
            
            # Use service role to bypass RLS for fetching user data
            from supabase import create_client
            from settings import settings
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            
            # Query by id (which is the UUID we stored in JWT sub claim)
            response = supabase.table("students").select("*").eq("id", user_id).execute()
            
            student_data = response.data[0] if response.data else {}
            
            return AuthUser(
                user_id=user_id,
                email=email,
                role="student",
                student_data=student_data
            )
        except Exception as e:
            logger.warning(f"Optional auth failed: {str(e)}")
            return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        data: Dictionary containing user data (must include 'sub' and 'email')
        expires_delta: Token expiration in seconds (default: 1 hour from settings)
        
    Returns:
        JWT token string
    """
    from datetime import timedelta
    
    if expires_delta is None:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    
    payload = {
        **data,  # Include all data (sub, email, role)
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "aud": "authenticated"
    }
    
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.ALGORITHM)
    return token


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    import bcrypt
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    import bcrypt
    
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
