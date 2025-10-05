"""
Models package for BharatAce backend
Contains Pydantic models for data validation
"""

from .admin import (
    AdminCreate,
    AdminLogin,
    AdminResponse,
    AdminToken,
    AdminUpdate,
    AdminRole,
    AdminPermissions,
    BulkImportStudent,
    BulkImportResult,
    DashboardStats,
    EnrollmentTrend,
    DepartmentDistribution,
    CGPADistribution,
    AIUsageStats,
    DashboardData
)

__all__ = [
    "AdminCreate",
    "AdminLogin",
    "AdminResponse",
    "AdminToken",
    "AdminUpdate",
    "AdminRole",
    "AdminPermissions",
    "BulkImportStudent",
    "BulkImportResult",
    "DashboardStats",
    "EnrollmentTrend",
    "DepartmentDistribution",
    "CGPADistribution",
    "AIUsageStats",
    "DashboardData"
]
