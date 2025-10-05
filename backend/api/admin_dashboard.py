"""
Admin Dashboard API
Provides analytics and statistics for admin panel
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from database import get_supabase_admin
from api.admin_auth import verify_admin_token
from admin_models.admin import (
    DashboardData, DashboardStats, EnrollmentTrend,
    DepartmentDistribution, CGPADistribution, AIUsageStats
)
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get dashboard statistics
    """
    supabase = get_supabase_admin()
    
    try:
        # Get total students
        students = supabase.table("students").select("id, cgpa").execute()
        total_students = len(students.data) if students.data else 0
        
        # Calculate average CGPA
        avg_cgpa = 0.0
        if students.data:
            cgpas = [s["cgpa"] for s in students.data if s.get("cgpa")]
            avg_cgpa = sum(cgpas) / len(cgpas) if cgpas else 0.0
        
        # Get total faculty
        faculty = supabase.table("faculty").select("id", count="exact").execute()
        total_faculty = faculty.count if hasattr(faculty, 'count') else 0
        
        # Get total departments
        departments = supabase.table("departments").select("id", count="exact").execute()
        total_departments = departments.count if hasattr(departments, 'count') else 0
        
        # Get total subjects
        subjects = supabase.table("subjects").select("id", count="exact").execute()
        total_subjects = subjects.count if hasattr(subjects, 'count') else 0
        
        # Calculate average attendance
        attendance_records = supabase.table("attendance").select("status").execute()
        avg_attendance = 0.0
        if attendance_records.data:
            present_count = sum(1 for a in attendance_records.data if a["status"] == "present")
            avg_attendance = (present_count / len(attendance_records.data)) * 100 if attendance_records.data else 0.0
        
        # Calculate fee collection rate
        fees = supabase.table("fees").select("amount_paid, total_amount").execute()
        fee_collection_rate = 0.0
        pending_amount = 0.0
        if fees.data:
            total_due = sum(f["total_amount"] for f in fees.data)
            total_paid = sum(f["amount_paid"] for f in fees.data)
            fee_collection_rate = (total_paid / total_due * 100) if total_due > 0 else 0.0
            pending_amount = total_due - total_paid
        
        # Get active events
        active_events = supabase.table("events").select("id").gte("event_date", datetime.now().date().isoformat()).execute()
        total_events = len(active_events.data) if active_events.data else 0
        
        # Students with attendance shortage (< 75%)
        attendance_summary = supabase.table("attendance").select("student_id, status").execute()
        students_with_shortage = 0
        if attendance_summary.data:
            student_attendance = {}
            for record in attendance_summary.data:
                sid = record["student_id"]
                if sid not in student_attendance:
                    student_attendance[sid] = {"present": 0, "total": 0}
                student_attendance[sid]["total"] += 1
                if record["status"] == "present":
                    student_attendance[sid]["present"] += 1
            
            for sid, data in student_attendance.items():
                if data["total"] > 0:
                    percentage = (data["present"] / data["total"]) * 100
                    if percentage < 75:
                        students_with_shortage += 1
        
        return DashboardStats(
            total_students=total_students,
            total_faculty=total_faculty,
            total_departments=total_departments,
            total_subjects=total_subjects,
            average_cgpa=round(avg_cgpa, 2),
            average_attendance=round(avg_attendance, 2),
            fee_collection_rate=round(fee_collection_rate, 2),
            active_events=total_events,
            pending_fee_amount=round(pending_amount, 2),
            students_with_shortage=students_with_shortage
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enrollment-trend", response_model=List[EnrollmentTrend])
async def get_enrollment_trend(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get student enrollment trend for last 12 months
    """
    supabase = get_supabase_admin()
    
    try:
        # Get all students with created_at
        students = supabase.table("students").select("created_at").execute()
        
        if not students.data:
            return []
        
        # Group by month
        monthly_counts = {}
        for student in students.data:
            created = datetime.fromisoformat(student["created_at"].replace("Z", "+00:00"))
            month_key = created.strftime("%B")
            year = created.year
            
            key = f"{month_key}-{year}"
            if key not in monthly_counts:
                monthly_counts[key] = {"month": month_key, "year": year, "count": 0}
            monthly_counts[key]["count"] += 1
        
        # Convert to list and sort
        trend = [EnrollmentTrend(**data) for data in monthly_counts.values()]
        return sorted(trend, key=lambda x: (x.year, x.month))[-12:]  # Last 12 months
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/department-distribution", response_model=List[DepartmentDistribution])
async def get_department_distribution(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get student distribution across departments
    """
    supabase = get_supabase_admin()
    
    try:
        # Get all students with departments
        students = supabase.table("students").select("department_id, departments(name)").execute()
        
        if not students.data:
            return []
        
        # Count by department
        dept_counts = Counter()
        total = 0
        for student in students.data:
            if student.get("departments"):
                dept_name = student["departments"]["name"]
                dept_counts[dept_name] += 1
                total += 1
        
        # Calculate percentages
        distribution = []
        for dept, count in dept_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            distribution.append(DepartmentDistribution(
                department=dept,
                count=count,
                percentage=round(percentage, 2)
            ))
        
        return sorted(distribution, key=lambda x: x.count, reverse=True)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cgpa-distribution", response_model=List[CGPADistribution])
async def get_cgpa_distribution(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get CGPA distribution across ranges
    """
    supabase = get_supabase_admin()
    
    try:
        students = supabase.table("students").select("cgpa").execute()
        
        if not students.data:
            return []
        
        # Define CGPA ranges
        ranges = {
            "9.0-10.0": 0,
            "8.0-8.9": 0,
            "7.0-7.9": 0,
            "6.0-6.9": 0,
            "Below 6.0": 0
        }
        
        for student in students.data:
            cgpa = student.get("cgpa", 0)
            if cgpa >= 9.0:
                ranges["9.0-10.0"] += 1
            elif cgpa >= 8.0:
                ranges["8.0-8.9"] += 1
            elif cgpa >= 7.0:
                ranges["7.0-7.9"] += 1
            elif cgpa >= 6.0:
                ranges["6.0-6.9"] += 1
            else:
                ranges["Below 6.0"] += 1
        
        return [CGPADistribution(range=r, count=c) for r, c in ranges.items()]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-usage", response_model=AIUsageStats)
async def get_ai_usage_stats(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get AI agent usage statistics
    (Mock data for now - implement actual tracking later)
    """
    # TODO: Implement actual AI usage tracking
    # This would require logging AI queries to database
    
    return AIUsageStats(
        total_queries=1250,
        queries_today=47,
        most_asked_category="Attendance",
        average_response_time=1.2,
        tool_usage={
            "get_student_attendance": 450,
            "get_student_marks": 320,
            "search_knowledge_base": 280,
            "get_student_fees": 150,
            "get_upcoming_events": 50
        }
    )


@router.get("", response_model=DashboardData)
async def get_complete_dashboard(admin_data: Dict = Depends(verify_admin_token)):
    """
    Get complete dashboard data
    """
    try:
        stats = await get_dashboard_stats(admin_data)
        enrollment = await get_enrollment_trend(admin_data)
        departments = await get_department_distribution(admin_data)
        cgpa = await get_cgpa_distribution(admin_data)
        ai_usage = await get_ai_usage_stats(admin_data)
        
        return DashboardData(
            stats=stats,
            enrollment_trend=enrollment,
            department_distribution=departments,
            cgpa_distribution=cgpa,
            ai_usage=ai_usage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
