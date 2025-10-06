"""
Student-specific API routes for frontend dashboard
Direct database queries - no AI overhead
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from database import get_supabase_admin
from auth import get_current_user, AuthUser

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/attendance/summary")
async def get_attendance_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get attendance summary for logged-in student"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        # Get all attendance records for the student
        attendance_response = supabase.table('attendance').select('*').eq('student_id', student_id).execute()
        
        records = attendance_response.data
        total_classes = len(records)
        
        if total_classes == 0:
            return {
                "total_classes": 0,
                "classes_attended": 0,
                "attendance_percentage": 0,
                "present_count": 0,
                "absent_count": 0,
                "late_count": 0
            }
        
        present_count = sum(1 for r in records if r['status'] == 'present')
        absent_count = sum(1 for r in records if r['status'] == 'absent')
        late_count = sum(1 for r in records if r['status'] == 'late')
        
        # Count present + late as attended
        classes_attended = present_count + late_count
        attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0
        
        return {
            "total_classes": total_classes,
            "classes_attended": classes_attended,
            "attendance_percentage": round(attendance_percentage, 2),
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")


@router.get("/fees/status")
async def get_fee_status(current_user: AuthUser = Depends(get_current_user)):
    """Get current semester fee status for logged-in student"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        # Get current semester fee record (latest)
        fees_response = supabase.table('fees')\
            .select('*')\
            .eq('student_id', student_id)\
            .order('semester', desc=True)\
            .limit(1)\
            .execute()
        
        if not fees_response.data:
            return {
                "total_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0,
                "status": "no_fees",
                "late_fee": 0,
                "due_date": None,
                "semester": None
            }
        
        fee_record = fees_response.data[0]
        total = fee_record.get('total_amount', 0)
        paid = fee_record.get('amount_paid', 0)  # Fixed: was 'paid_amount'
        
        return {
            "total_amount": total,
            "paid_amount": paid,
            "pending_amount": total - paid,
            "status": fee_record.get('payment_status', 'pending'),  # Fixed: was 'status'
            "late_fee": fee_record.get('late_fee', 0),
            "due_date": fee_record.get('due_date'),
            "semester": fee_record.get('semester')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fees: {str(e)}")


@router.get("/timetable/today")
async def get_today_timetable(current_user: AuthUser = Depends(get_current_user)):
    """Get today's class schedule for logged-in student"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        # Get current day of week
        today = datetime.now()
        # Convert day name to integer (0=Sunday, 1=Monday, ..., 6=Saturday)
        # Python's weekday() returns 0=Monday, so we need to convert
        day_number = (today.weekday() + 1) % 7  # Convert to 0=Sunday format
        
        # Get student's semester
        student_semester = current_user.student_data.get('semester', 1)
        
        # Get timetable for today (without join first)
        try:
            timetable_response = supabase.table('timetable')\
                .select('*')\
                .eq('semester', student_semester)\
                .eq('day_of_week', day_number)\
                .order('start_time')\
                .execute()
        except Exception as query_error:
            # If query fails, return empty schedule
            print(f"Timetable query error: {str(query_error)}")
            return []
        
        if not timetable_response.data:
            return []
        
        # Get subject IDs
        subject_ids = [entry['subject_id'] for entry in timetable_response.data if entry.get('subject_id')]
        
        # Fetch subjects separately
        subjects_dict = {}
        if subject_ids:
            try:
                subjects_response = supabase.table('subjects')\
                    .select('*')\
                    .in_('id', subject_ids)\
                    .execute()
                
                for subject in subjects_response.data:
                    subjects_dict[subject['id']] = subject
            except Exception as subject_error:
                print(f"Subjects query error: {str(subject_error)}")
                # Continue without subject details
        
        # Build schedule with subject details
        schedule = []
        for entry in timetable_response.data:
            subject_id = entry.get('subject_id')
            subject = subjects_dict.get(subject_id, {})
            
            schedule.append({
                "id": entry['id'],
                "subject_name": subject.get('subject_name', 'Unknown Subject'),
                "subject_code": subject.get('subject_code', 'N/A'),
                "room": entry.get('room_number', 'TBA'),
                "start_time": entry.get('start_time', ''),
                "end_time": entry.get('end_time', ''),
                "session_type": entry.get('session_type', 'lecture')
            })
        
        return schedule
    except Exception as e:
        print(f"Timetable endpoint error: {str(e)}")
        # Return empty array instead of raising exception
        return []


@router.get("/library/loans")
async def get_library_loans(current_user: AuthUser = Depends(get_current_user)):
    """Get active and recent library book loans for logged-in student"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        # Get all loans for the student with book details
        loans_response = supabase.table('book_loans')\
            .select('*, library_books(title, author, isbn)')\
            .eq('student_id', student_id)\
            .order('issue_date', desc=True)\
            .execute()
        
        loans = []
        for loan in loans_response.data:
            book = loan.get('library_books', {})
            loans.append({
                "id": loan['id'],
                "book": {
                    "title": book.get('title', 'Unknown Book'),
                    "author": book.get('author', 'Unknown Author'),
                    "isbn": book.get('isbn', '')
                },
                "issue_date": loan['issue_date'],
                "due_date": loan['due_date'],
                "return_date": loan.get('return_date'),
                "status": 'returned' if loan.get('return_date') else 'active'
            })
        
        active_loans = [l for l in loans if l['status'] == 'active']
        
        return {
            "loans": loans,
            "active_count": len(active_loans),
            "total_count": len(loans)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching library loans: {str(e)}")


@router.get("/events/upcoming")
async def get_upcoming_events():
    """Get upcoming events (next 30 days)"""
    supabase = get_supabase_admin()
    
    try:
        # Get events from today onwards
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        
        events_response = supabase.table('events')\
            .select('*')\
            .gte('start_date', today)\
            .lte('start_date', end_date)\
            .order('start_date')\
            .execute()
        
        return {
            "events": events_response.data,
            "count": len(events_response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@router.get("/events/my-events")
async def get_my_events(current_user: AuthUser = Depends(get_current_user)):
    """Get student's registered events"""
    supabase = get_supabase_admin()
    
    try:
        # Get student's event registrations with event details
        registrations_response = supabase.table('event_participation')\
            .select('*, events(*)')\
            .eq('student_id', current_user.student_id)\
            .eq('attendance_status', 'registered')\
            .order('registration_date', desc=True)\
            .execute()
        
        # Extract event data from registrations
        registered_events = []
        upcoming_events = []
        past_events = []
        
        today = date.today()
        
        for registration in registrations_response.data:
            if registration.get('events'):
                event = registration['events']
                event['registration_date'] = registration['registration_date']
                event['registration_id'] = registration['id']
                
                # Categorize by date
                event_date = date.fromisoformat(event['start_date'].split('T')[0])
                if event_date >= today:
                    upcoming_events.append(event)
                else:
                    past_events.append(event)
                
                registered_events.append(event)
        
        return {
            "all_events": registered_events,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "total_registered": len(registered_events),
            "upcoming_count": len(upcoming_events),
            "past_count": len(past_events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching registered events: {str(e)}")


@router.get("/marks/summary")
async def get_marks_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get marks summary and CGPA for logged-in student"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        # Get all marks with subject details
        marks_response = supabase.table('marks')\
            .select('*, subjects(subject_name, subject_code, credits, semester)')\
            .eq('student_id', student_id)\
            .order('exam_date', desc=True)\
            .execute()
        
        marks = marks_response.data
        
        if not marks:
            return {
                "total_subjects": 0,
                "average_percentage": 0,
                "cgpa": 0,
                "recent_marks": []
            }
        
        # Calculate average percentage
        total_percentage = sum(m.get('percentage', 0) for m in marks)
        avg_percentage = total_percentage / len(marks) if marks else 0
        
        # Calculate CGPA (assuming 10 point scale)
        cgpa = (avg_percentage / 10) if avg_percentage > 0 else 0
        
        # Get recent marks (last 5)
        recent = []
        for mark in marks[:5]:
            subject = mark.get('subjects', {})
            recent.append({
                "subject_name": subject.get('subject_name', 'Unknown'),
                "subject_code": subject.get('subject_code', ''),
                "marks_obtained": mark.get('marks_obtained', 0),
                "total_marks": mark.get('total_marks', 100),
                "percentage": mark.get('percentage', 0),
                "exam_date": mark.get('exam_date')
            })
        
        return {
            "total_subjects": len(marks),
            "average_percentage": round(avg_percentage, 2),
            "cgpa": round(cgpa, 2),
            "recent_marks": recent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching marks: {str(e)}")


@router.get("/profile")
async def get_student_profile(current_user: AuthUser = Depends(get_current_user)):
    """Get complete student profile"""
    supabase = get_supabase_admin()
    student_id = current_user.student_id
    
    try:
        student_response = supabase.table('students')\
            .select('*')\
            .eq('id', student_id)\
            .single()\
            .execute()
        
        return student_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")
