"""
Admin User Models
Pydantic models for admin authentication and management
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    """Admin role types"""
    SUPER_ADMIN = "super_admin"  # Platform-level access
    INSTITUTION_ADMIN = "institution_admin"  # Per-college access
    DEPARTMENT_ADMIN = "department_admin"  # Department-level access
    FACULTY = "faculty"  # Limited access


class AdminPermissions(BaseModel):
    """Admin permissions"""
    can_manage_institutions: bool = False
    can_manage_students: bool = False
    can_manage_faculty: bool = False
    can_enter_marks: bool = False
    can_mark_attendance: bool = False
    can_manage_fees: bool = False
    can_manage_library: bool = False
    can_manage_events: bool = False
    can_manage_knowledge_base: bool = False
    can_view_reports: bool = False
    can_export_data: bool = False
    can_delete_records: bool = False


class AdminCreate(BaseModel):
    """Create admin user"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: AdminRole
    institution_id: Optional[str] = None
    permissions: Optional[Dict] = None


class AdminLogin(BaseModel):
    """Admin login credentials"""
    email: EmailStr
    password: str


class AdminUpdate(BaseModel):
    """Update admin user"""
    full_name: Optional[str] = None
    role: Optional[AdminRole] = None
    permissions: Optional[Dict] = None
    is_active: Optional[bool] = None


class AdminResponse(BaseModel):
    """Admin user response"""
    id: str
    email: str
    full_name: str
    role: AdminRole
    institution_id: Optional[str]
    permissions: Dict
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminToken(BaseModel):
    """Admin authentication token response"""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse


# Bulk Import Models

class BulkImportStudent(BaseModel):
    """Student data for bulk import"""
    full_name: str
    email: EmailStr
    roll_number: str
    department: str
    semester: int = Field(..., ge=1, le=10)
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None


class BulkImportResult(BaseModel):
    """Result of bulk import operation"""
    success: bool
    total_records: int
    successful: int
    failed: int
    errors: List[Dict] = []
    imported_ids: List[str] = []


# Dashboard Models

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_students: int
    total_faculty: int
    total_departments: int
    total_subjects: int
    average_cgpa: float
    average_attendance: float
    fee_collection_rate: float
    active_events: int
    pending_fee_amount: float
    students_with_shortage: int
    
    
class EnrollmentTrend(BaseModel):
    """Student enrollment trend"""
    month: str
    year: int
    count: int


class DepartmentDistribution(BaseModel):
    """Department-wise student distribution"""
    department: str
    count: int
    percentage: float


class CGPADistribution(BaseModel):
    """CGPA distribution"""
    range: str  # "9.0-10.0", "8.0-8.9", etc.
    count: int


class AIUsageStats(BaseModel):
    """AI agent usage statistics"""
    total_queries: int
    queries_today: int
    most_asked_category: str
    average_response_time: float
    tool_usage: Dict[str, int]  # tool_name -> count
    

class DashboardData(BaseModel):
    """Complete dashboard data"""
    stats: DashboardStats
    enrollment_trend: List[EnrollmentTrend]
    department_distribution: List[DepartmentDistribution]
    cgpa_distribution: List[CGPADistribution]
    ai_usage: AIUsageStats
