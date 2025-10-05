"""
Timetable Tool
Retrieves college and student-specific timetable information.
"""

from typing import Dict, Any, List, Optional
import logging
from database import get_supabase_admin

logger = logging.getLogger(__name__)

DAYS_MAP = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday"
}


def get_full_timetable(semester: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the complete college timetable.
    
    Args:
        semester: Optional semester number to filter
        
    Returns:
        Dictionary containing timetable organized by day and time
    """
    try:
        supabase = get_supabase_admin()
        
        # Build query
        query = supabase.table("timetable")\
            .select("*, subjects(subject_name, subject_code, instructor_name, department)")\
            .order("day_of_week")\
            .order("start_time")
        
        if semester:
            query = query.eq("semester", semester)
        
        response = query.execute()
        
        if not response.data:
            return {
                "timetable": {},
                "message": "No timetable found",
                "success": True
            }
        
        # Organize by day of week
        timetable_by_day = {}
        
        for entry in response.data:
            day_num = entry['day_of_week']
            day_name = DAYS_MAP.get(day_num, "Unknown")
            
            if day_name not in timetable_by_day:
                timetable_by_day[day_name] = []
            
            timetable_by_day[day_name].append({
                "subject_name": entry['subjects']['subject_name'],
                "subject_code": entry['subjects']['subject_code'],
                "instructor": entry['subjects']['instructor_name'],
                "department": entry['subjects']['department'],
                "start_time": entry['start_time'],
                "end_time": entry['end_time'],
                "room_number": entry['room_number'],
                "session_type": entry['session_type'],
                "semester": entry['semester']
            })
        
        logger.info(f"Retrieved timetable with {len(response.data)} entries")
        
        return {
            "timetable": timetable_by_day,
            "total_entries": len(response.data),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting timetable: {str(e)}")
        return {
            "timetable": {},
            "success": False,
            "error": str(e)
        }


def get_student_timetable(student_id: str) -> Dict[str, Any]:
    """
    Get timetable for a specific student based on their semester.
    
    Args:
        student_id: The student's database ID
        
    Returns:
        Dictionary containing the student's personalized timetable
    """
    try:
        supabase = get_supabase_admin()
        
        # Get student's semester
        student_response = supabase.table("students")\
            .select("semester, course, department")\
            .eq("id", student_id)\
            .execute()
        
        if not student_response.data:
            return {
                "timetable": {},
                "success": False,
                "message": "Student not found"
            }
        
        student = student_response.data[0]
        semester = student['semester']
        
        # Get timetable for the student's semester
        result = get_full_timetable(semester=semester)
        
        if result['success']:
            result['student_info'] = {
                "semester": semester,
                "course": student['course'],
                "department": student['department']
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting student timetable: {str(e)}")
        return {
            "timetable": {},
            "success": False,
            "error": str(e)
        }


def get_timetable_for_day(day: str, semester: Optional[int] = None) -> Dict[str, Any]:
    """
    Get timetable for a specific day of the week.
    
    Args:
        day: Day name (e.g., "Monday", "Tuesday")
        semester: Optional semester number
        
    Returns:
        Dictionary with schedule for the specified day
    """
    try:
        # Convert day name to number
        day_num = None
        for num, name in DAYS_MAP.items():
            if name.lower() == day.lower():
                day_num = num
                break
        
        if day_num is None:
            return {
                "schedule": [],
                "success": False,
                "message": f"Invalid day: {day}. Use Monday, Tuesday, etc."
            }
        
        supabase = get_supabase_admin()
        
        query = supabase.table("timetable")\
            .select("*, subjects(subject_name, subject_code, instructor_name)")\
            .eq("day_of_week", day_num)\
            .order("start_time")
        
        if semester:
            query = query.eq("semester", semester)
        
        response = query.execute()
        
        schedule = []
        for entry in response.data:
            schedule.append({
                "subject_name": entry['subjects']['subject_name'],
                "subject_code": entry['subjects']['subject_code'],
                "instructor": entry['subjects']['instructor_name'],
                "start_time": entry['start_time'],
                "end_time": entry['end_time'],
                "room_number": entry['room_number'],
                "session_type": entry['session_type'],
                "semester": entry['semester']
            })
        
        return {
            "day": day.capitalize(),
            "schedule": schedule,
            "total_classes": len(schedule),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting day timetable: {str(e)}")
        return {
            "schedule": [],
            "success": False,
            "error": str(e)
        }


def get_next_class(student_id: str) -> Dict[str, Any]:
    """
    Get the next upcoming class for a student.
    
    Args:
        student_id: The student's database ID
        
    Returns:
        Dictionary with next class information
    """
    try:
        from datetime import datetime, time
        
        # Get current day and time
        now = datetime.now()
        current_day = now.weekday() + 1  # Monday = 1, Sunday = 0
        current_time = now.time()
        
        # Get student's timetable
        timetable_result = get_student_timetable(student_id)
        
        if not timetable_result['success']:
            return timetable_result
        
        timetable = timetable_result['timetable']
        current_day_name = DAYS_MAP.get(current_day, "Unknown")
        
        # Find next class today
        if current_day_name in timetable:
            for class_entry in timetable[current_day_name]:
                class_start = datetime.strptime(class_entry['start_time'], "%H:%M:%S").time()
                if class_start > current_time:
                    return {
                        "next_class": class_entry,
                        "day": current_day_name,
                        "is_today": True,
                        "success": True
                    }
        
        # If no class today, find next class in upcoming days
        for day_offset in range(1, 8):
            next_day_num = (current_day + day_offset) % 7
            next_day_name = DAYS_MAP.get(next_day_num)
            
            if next_day_name in timetable and len(timetable[next_day_name]) > 0:
                return {
                    "next_class": timetable[next_day_name][0],
                    "day": next_day_name,
                    "is_today": False,
                    "days_away": day_offset,
                    "success": True
                }
        
        return {
            "next_class": None,
            "message": "No upcoming classes found",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting next class: {str(e)}")
        return {
            "next_class": None,
            "success": False,
            "error": str(e)
        }


def find_free_slots(semester: int, day: Optional[str] = None) -> Dict[str, Any]:
    """
    Find free time slots when no classes are scheduled.
    
    Args:
        semester: Semester number
        day: Optional specific day to check
        
    Returns:
        Dictionary with free slots information
    """
    try:
        # Define college hours (8 AM to 6 PM)
        college_start = "08:00:00"
        college_end = "18:00:00"
        
        if day:
            timetable_result = get_timetable_for_day(day, semester)
            if not timetable_result['success']:
                return timetable_result
            
            schedule = timetable_result['schedule']
            free_slots = calculate_free_slots(schedule, college_start, college_end)
            
            return {
                "day": day,
                "free_slots": free_slots,
                "total_free_hours": sum(slot['duration_minutes'] for slot in free_slots) / 60,
                "success": True
            }
        else:
            # Get full week timetable
            full_timetable = get_full_timetable(semester)
            if not full_timetable['success']:
                return full_timetable
            
            weekly_free_slots = {}
            for day_name, schedule in full_timetable['timetable'].items():
                free_slots = calculate_free_slots(schedule, college_start, college_end)
                weekly_free_slots[day_name] = free_slots
            
            return {
                "weekly_free_slots": weekly_free_slots,
                "success": True
            }
        
    except Exception as e:
        logger.error(f"Error finding free slots: {str(e)}")
        return {
            "free_slots": [],
            "success": False,
            "error": str(e)
        }


def calculate_free_slots(schedule: List[Dict], start_time: str, end_time: str) -> List[Dict]:
    """Helper function to calculate free slots between classes"""
    from datetime import datetime, timedelta
    
    if not schedule:
        return [{
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": 600  # Full day
        }]
    
    free_slots = []
    current_time = datetime.strptime(start_time, "%H:%M:%S")
    end_time_obj = datetime.strptime(end_time, "%H:%M:%S")
    
    for class_entry in sorted(schedule, key=lambda x: x['start_time']):
        class_start = datetime.strptime(class_entry['start_time'], "%H:%M:%S")
        
        if class_start > current_time:
            duration = (class_start - current_time).total_seconds() / 60
            if duration >= 30:  # Only include gaps of 30 minutes or more
                free_slots.append({
                    "start_time": current_time.strftime("%H:%M:%S"),
                    "end_time": class_start.strftime("%H:%M:%S"),
                    "duration_minutes": int(duration)
                })
        
        class_end = datetime.strptime(class_entry['end_time'], "%H:%M:%S")
        current_time = max(current_time, class_end)
    
    # Check for free time after last class
    if current_time < end_time_obj:
        duration = (end_time_obj - current_time).total_seconds() / 60
        if duration >= 30:
            free_slots.append({
                "start_time": current_time.strftime("%H:%M:%S"),
                "end_time": end_time,
                "duration_minutes": int(duration)
            })
    
    return free_slots

