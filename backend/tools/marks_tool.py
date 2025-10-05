"""
Marks Tool
Retrieves and analyzes student marks/grades data.
"""

from typing import Dict, Any, List, Optional
import logging
from database import get_supabase_admin

logger = logging.getLogger(__name__)


def get_student_marks(student_id: str, subject_id: Optional[str] = None, semester: Optional[int] = None) -> Dict[str, Any]:
    """
    Get marks/grades for a student.
    
    Args:
        student_id: The student's database ID (UUID)
        subject_id: Optional subject ID to filter by specific subject
        semester: Optional semester number to filter
        
    Returns:
        Dictionary containing marks records and statistics
    """
    try:
        supabase = get_supabase_admin()
        
        # Build query
        query = supabase.table("marks")\
            .select("*, subjects(subject_name, subject_code, credits, semester)")\
            .eq("student_id", student_id)\
            .order("exam_date", desc=True)
        
        if subject_id:
            query = query.eq("subject_id", subject_id)
        
        response = query.execute()
        
        if not response.data:
            return {
                "records": [],
                "statistics": {},
                "message": "No marks found",
                "success": True
            }
        
        records = response.data
        
        # Filter by semester if provided
        if semester:
            records = [r for r in records if r['subjects']['semester'] == semester]
        
        # Calculate statistics
        total_exams = len(records)
        total_marks_obtained = sum(r['obtained_marks'] for r in records)
        total_max_marks = sum(r['max_marks'] for r in records)
        
        overall_percentage = (total_marks_obtained / total_max_marks * 100) if total_max_marks > 0 else 0.0
        
        # Subject-wise breakdown
        subject_wise = {}
        for record in records:
            subject_name = record['subjects']['subject_name']
            if subject_name not in subject_wise:
                subject_wise[subject_name] = {
                    "subject_code": record['subjects']['subject_code'],
                    "credits": record['subjects']['credits'],
                    "exams": []
                }
            
            subject_wise[subject_name]["exams"].append({
                "exam_type": record['exam_type'],
                "obtained_marks": float(record['obtained_marks']),
                "max_marks": record['max_marks'],
                "percentage": round(float(record['obtained_marks']) / record['max_marks'] * 100, 2),
                "exam_date": record['exam_date']
            })
        
        # Calculate average per subject
        for subject, data in subject_wise.items():
            total_obtained = sum(e['obtained_marks'] for e in data['exams'])
            total_max = sum(e['max_marks'] for e in data['exams'])
            data['average_percentage'] = round((total_obtained / total_max * 100) if total_max > 0 else 0.0, 2)
        
        logger.info(f"Retrieved marks for student {student_id}: {overall_percentage:.2f}%")
        
        return {
            "records": records,
            "statistics": {
                "total_exams": total_exams,
                "total_marks_obtained": round(total_marks_obtained, 2),
                "total_max_marks": total_max_marks,
                "overall_percentage": round(overall_percentage, 2)
            },
            "subject_wise": subject_wise,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting marks: {str(e)}")
        return {
            "records": [],
            "statistics": {},
            "success": False,
            "error": str(e)
        }


def calculate_cgpa(student_id: str) -> Dict[str, Any]:
    """
    Calculate CGPA (Cumulative Grade Point Average) for a student.
    
    Uses a 10-point scale:
    - 90-100: 10 (O - Outstanding)
    - 80-89: 9 (A+ - Excellent)
    - 70-79: 8 (A - Very Good)
    - 60-69: 7 (B+ - Good)
    - 50-59: 6 (B - Above Average)
    - 40-49: 5 (C - Average)
    - 0-39: 0 (F - Fail)
    
    Args:
        student_id: The student's database ID
        
    Returns:
        Dictionary with CGPA and detailed breakdown
    """
    try:
        marks_result = get_student_marks(student_id)
        
        if not marks_result['success'] or not marks_result['records']:
            return {
                "cgpa": 0.0,
                "total_credits": 0,
                "semester_wise": {},
                "message": "No marks available for CGPA calculation",
                "success": True
            }
        
        # Group by semester
        semester_data = {}
        
        for record in marks_result['records']:
            subject = record['subjects']
            semester = subject['semester']
            
            if semester not in semester_data:
                semester_data[semester] = {
                    "subjects": {},
                    "total_credits": 0,
                    "weighted_gpa": 0.0
                }
            
            subject_name = subject['subject_name']
            credits = subject['credits']
            
            # Calculate percentage for this exam
            percentage = (float(record['obtained_marks']) / record['max_marks'] * 100)
            
            # Store or update subject data
            if subject_name not in semester_data[semester]["subjects"]:
                semester_data[semester]["subjects"][subject_name] = {
                    "credits": credits,
                    "percentages": [],
                    "subject_code": subject['subject_code']
                }
            
            semester_data[semester]["subjects"][subject_name]["percentages"].append(percentage)
        
        # Calculate SGPA for each semester
        semester_wise_gpa = {}
        total_credits_overall = 0
        weighted_gpa_overall = 0.0
        
        for semester, data in semester_data.items():
            semester_credits = 0
            semester_weighted_gpa = 0.0
            
            for subject_name, subject_info in data["subjects"].items():
                # Average percentage across all exams for this subject
                avg_percentage = sum(subject_info["percentages"]) / len(subject_info["percentages"])
                
                # Convert percentage to grade point
                grade_point = percentage_to_grade_point(avg_percentage)
                
                credits = subject_info["credits"]
                semester_credits += credits
                semester_weighted_gpa += grade_point * credits
            
            sgpa = (semester_weighted_gpa / semester_credits) if semester_credits > 0 else 0.0
            
            semester_wise_gpa[f"Semester {semester}"] = {
                "sgpa": round(sgpa, 2),
                "credits": semester_credits,
                "grade": grade_point_to_letter(sgpa)
            }
            
            total_credits_overall += semester_credits
            weighted_gpa_overall += semester_weighted_gpa
        
        # Calculate overall CGPA
        cgpa = (weighted_gpa_overall / total_credits_overall) if total_credits_overall > 0 else 0.0
        
        logger.info(f"Calculated CGPA for student {student_id}: {cgpa:.2f}")
        
        return {
            "cgpa": round(cgpa, 2),
            "grade": grade_point_to_letter(cgpa),
            "total_credits": total_credits_overall,
            "semester_wise": semester_wise_gpa,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error calculating CGPA: {str(e)}")
        return {
            "cgpa": 0.0,
            "total_credits": 0,
            "success": False,
            "error": str(e)
        }


def calculate_sgpa(student_id: str, semester: int) -> Dict[str, Any]:
    """
    Calculate SGPA (Semester Grade Point Average) for a specific semester.
    
    Args:
        student_id: The student's database ID
        semester: Semester number
        
    Returns:
        Dictionary with SGPA and subject-wise breakdown
    """
    try:
        marks_result = get_student_marks(student_id, semester=semester)
        
        if not marks_result['success'] or not marks_result['records']:
            return {
                "sgpa": 0.0,
                "semester": semester,
                "subjects": [],
                "message": f"No marks found for semester {semester}",
                "success": True
            }
        
        # Group by subject
        subject_data = {}
        
        for record in marks_result['records']:
            subject = record['subjects']
            subject_name = subject['subject_name']
            credits = subject['credits']
            
            percentage = (float(record['obtained_marks']) / record['max_marks'] * 100)
            
            if subject_name not in subject_data:
                subject_data[subject_name] = {
                    "credits": credits,
                    "percentages": [],
                    "subject_code": subject['subject_code']
                }
            
            subject_data[subject_name]["percentages"].append(percentage)
        
        # Calculate SGPA
        total_credits = 0
        weighted_gpa = 0.0
        subject_breakdown = []
        
        for subject_name, data in subject_data.items():
            avg_percentage = sum(data["percentages"]) / len(data["percentages"])
            grade_point = percentage_to_grade_point(avg_percentage)
            credits = data["credits"]
            
            total_credits += credits
            weighted_gpa += grade_point * credits
            
            subject_breakdown.append({
                "subject_name": subject_name,
                "subject_code": data["subject_code"],
                "percentage": round(avg_percentage, 2),
                "grade_point": round(grade_point, 2),
                "grade": grade_point_to_letter(grade_point),
                "credits": credits
            })
        
        sgpa = (weighted_gpa / total_credits) if total_credits > 0 else 0.0
        
        logger.info(f"Calculated SGPA for student {student_id}, semester {semester}: {sgpa:.2f}")
        
        return {
            "sgpa": round(sgpa, 2),
            "semester": semester,
            "grade": grade_point_to_letter(sgpa),
            "total_credits": total_credits,
            "subjects": subject_breakdown,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error calculating SGPA: {str(e)}")
        return {
            "sgpa": 0.0,
            "semester": semester,
            "success": False,
            "error": str(e)
        }


def percentage_to_grade_point(percentage: float) -> float:
    """Convert percentage to grade point (10-point scale)"""
    if percentage >= 90:
        return 10.0
    elif percentage >= 80:
        return 9.0
    elif percentage >= 70:
        return 8.0
    elif percentage >= 60:
        return 7.0
    elif percentage >= 50:
        return 6.0
    elif percentage >= 40:
        return 5.0
    else:
        return 0.0


def grade_point_to_letter(gpa: float) -> str:
    """Convert grade point to letter grade"""
    if gpa >= 9.0:
        return "O"  # Outstanding
    elif gpa >= 8.0:
        return "A+"  # Excellent
    elif gpa >= 7.0:
        return "A"  # Very Good
    elif gpa >= 6.0:
        return "B+"  # Good
    elif gpa >= 5.0:
        return "B"  # Above Average
    elif gpa >= 4.0:
        return "C"  # Average
    else:
        return "F"  # Fail


def get_rank_in_class(student_id: str, semester: int) -> Dict[str, Any]:
    """
    Calculate student's rank in their class for a given semester.
    
    Args:
        student_id: The student's database ID
        semester: Semester number
        
    Returns:
        Dictionary with rank information
    """
    try:
        supabase = get_supabase_admin()
        
        # Get student's course and semester
        student_response = supabase.table("students")\
            .select("course, semester")\
            .eq("id", student_id)\
            .execute()
        
        if not student_response.data:
            return {
                "rank": None,
                "total_students": 0,
                "success": False,
                "message": "Student not found"
            }
        
        course = student_response.data[0]['course']
        
        # Get all students in same course and semester
        students_response = supabase.table("students")\
            .select("id")\
            .eq("course", course)\
            .eq("semester", semester)\
            .execute()
        
        # Calculate SGPA for all students
        student_sgpas = []
        for student in students_response.data:
            sgpa_result = calculate_sgpa(student['id'], semester)
            if sgpa_result['success']:
                student_sgpas.append({
                    "student_id": student['id'],
                    "sgpa": sgpa_result['sgpa']
                })
        
        # Sort by SGPA descending
        student_sgpas.sort(key=lambda x: x['sgpa'], reverse=True)
        
        # Find current student's rank
        rank = None
        for idx, student in enumerate(student_sgpas, 1):
            if student['student_id'] == student_id:
                rank = idx
                break
        
        return {
            "rank": rank,
            "total_students": len(student_sgpas),
            "percentile": round((1 - (rank - 1) / len(student_sgpas)) * 100, 2) if rank else None,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error calculating rank: {str(e)}")
        return {
            "rank": None,
            "total_students": 0,
            "success": False,
            "error": str(e)
        }

