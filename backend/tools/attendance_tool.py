"""
Attendance Tool
Retrieves and analyzes student attendance data.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from database import get_supabase_admin

logger = logging.getLogger(__name__)


def get_student_attendance(student_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get attendance records for a student.
    
    Args:
        student_id: The student's database ID (UUID)
        subject_id: Optional subject ID to filter by specific subject
        
    Returns:
        Dictionary containing attendance records and statistics
        
    Example:
        result = get_student_attendance("uuid-here")
        # Returns: {
        #     "records": [...],
        #     "statistics": {
        #         "total_classes": 45,
        #         "attended": 40,
        #         "percentage": 88.89
        #     }
        # }
    """
    try:
        supabase = get_supabase_admin()
        
        # Build query
        query = supabase.table("attendance")\
            .select("*, subjects(subject_name, subject_code)")\
            .eq("student_id", student_id)\
            .order("date", desc=True)
        
        # Add subject filter if provided
        if subject_id:
            query = query.eq("subject_id", subject_id)
        
        response = query.execute()
        
        if not response.data:
            return {
                "records": [],
                "statistics": {
                    "total_classes": 0,
                    "attended": 0,
                    "percentage": 0.0
                },
                "message": "No attendance records found",
                "success": True
            }
        
        # Calculate statistics
        records = response.data
        total_classes = len(records)
        present_count = len([r for r in records if r['status'] == 'present'])
        late_count = len([r for r in records if r['status'] == 'late'])
        absent_count = len([r for r in records if r['status'] == 'absent'])
        
        # Calculate percentage (present + late counts as attended)
        attended = present_count + late_count
        percentage = (attended / total_classes * 100) if total_classes > 0 else 0.0
        
        # Group by subject
        subject_wise = {}
        for record in records:
            subject_name = record['subjects']['subject_name']
            if subject_name not in subject_wise:
                subject_wise[subject_name] = {
                    "total": 0,
                    "present": 0,
                    "late": 0,
                    "absent": 0
                }
            
            subject_wise[subject_name]["total"] += 1
            subject_wise[subject_name][record['status']] += 1
        
        # Calculate subject-wise percentages
        for subject in subject_wise.values():
            attended_classes = subject['present'] + subject['late']
            subject['percentage'] = round(
                (attended_classes / subject['total'] * 100) if subject['total'] > 0 else 0.0,
                2
            )
        
        logger.info(f"Retrieved attendance for student {student_id}: {percentage:.2f}%")
        
        return {
            "records": records,
            "statistics": {
                "total_classes": total_classes,
                "attended": attended,
                "present": present_count,
                "late": late_count,
                "absent": absent_count,
                "percentage": round(percentage, 2)
            },
            "subject_wise": subject_wise,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting attendance: {str(e)}")
        return {
            "records": [],
            "statistics": {},
            "success": False,
            "error": str(e)
        }


def calculate_attendance_percentage(student_id: str, subject_id: Optional[str] = None) -> float:
    """
    Calculate attendance percentage for a student.
    
    Args:
        student_id: The student's database ID
        subject_id: Optional subject ID for subject-specific percentage
        
    Returns:
        Attendance percentage as a float
    """
    result = get_student_attendance(student_id, subject_id)
    
    if result['success']:
        return result['statistics'].get('percentage', 0.0)
    
    return 0.0


def get_attendance_by_date_range(
    student_id: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Get attendance records for a specific date range.
    
    Args:
        student_id: The student's database ID
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing filtered attendance records
    """
    try:
        supabase = get_supabase_admin()
        
        response = supabase.table("attendance")\
            .select("*, subjects(subject_name, subject_code)")\
            .eq("student_id", student_id)\
            .gte("date", start_date)\
            .lte("date", end_date)\
            .order("date", desc=True)\
            .execute()
        
        records = response.data
        total = len(records)
        attended = len([r for r in records if r['status'] in ['present', 'late']])
        percentage = (attended / total * 100) if total > 0 else 0.0
        
        return {
            "records": records,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "statistics": {
                "total_classes": total,
                "attended": attended,
                "percentage": round(percentage, 2)
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting attendance by date range: {str(e)}")
        return {
            "records": [],
            "success": False,
            "error": str(e)
        }


def check_attendance_shortage(student_id: str, required_percentage: float = 75.0) -> Dict[str, Any]:
    """
    Check if student has attendance shortage.
    
    Args:
        student_id: The student's database ID
        required_percentage: Minimum required attendance (default 75%)
        
    Returns:
        Dictionary with shortage information and warnings
    """
    result = get_student_attendance(student_id)
    
    if not result['success']:
        return result
    
    current_percentage = result['statistics']['percentage']
    has_shortage = current_percentage < required_percentage
    shortage = required_percentage - current_percentage if has_shortage else 0.0
    
    # Calculate classes needed to reach required percentage
    total_classes = result['statistics']['total_classes']
    attended = result['statistics']['attended']
    
    classes_needed = 0
    if has_shortage and total_classes > 0:
        # Formula: (attended + x) / (total + x) >= required/100
        # Solving: x >= (required*total - 100*attended) / (100 - required)
        numerator = (required_percentage * total_classes) - (100 * attended)
        denominator = 100 - required_percentage
        classes_needed = max(0, int(numerator / denominator) + 1)
    
    return {
        "has_shortage": has_shortage,
        "current_percentage": round(current_percentage, 2),
        "required_percentage": required_percentage,
        "shortage": round(shortage, 2),
        "classes_needed": classes_needed,
        "subject_wise_shortage": [
            {
                "subject": subject,
                "percentage": stats['percentage'],
                "has_shortage": stats['percentage'] < required_percentage
            }
            for subject, stats in result.get('subject_wise', {}).items()
        ],
        "success": True
    }

