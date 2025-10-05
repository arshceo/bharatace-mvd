from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from database import get_supabase_admin
from auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

# ================== Pydantic Models ==================

class StudentCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    roll_number: str
    branch: str
    semester: int
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    phone: Optional[str] = None
    cgpa: Optional[float] = None

class MarkCreate(BaseModel):
    student_id: str
    subject_id: str
    exam_type: str
    obtained_marks: float
    max_marks: float
    exam_date: date

class MarkUpdate(BaseModel):
    obtained_marks: Optional[float] = None
    max_marks: Optional[float] = None
    exam_type: Optional[str] = None
    exam_date: Optional[date] = None

class AttendanceCreate(BaseModel):
    student_id: str
    subject_id: str
    date: date
    status: str  # present, absent, late

class FeeCreate(BaseModel):
    student_id: str
    semester: int
    amount: float
    due_date: date
    status: str  # paid, partial, overdue

class PaymentRecord(BaseModel):
    amount: float
    payment_date: date
    payment_method: Optional[str] = "cash"

class SubjectCreate(BaseModel):
    name: str
    code: str
    semester: int
    credits: int
    branch: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    event_type: str

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category: Optional[str] = None
    quantity: int = 1

class LoanCreate(BaseModel):
    student_id: str
    book_id: str
    due_date: date


# ================== Student Management ==================

@router.get("/students")
async def get_all_students(
    search: Optional[str] = None,
    branch: Optional[str] = None,
    semester: Optional[int] = None
):
    """Get all students with optional filters"""
    supabase = get_supabase_admin()
    
    query = supabase.table('students').select('*')
    
    if search:
        query = query.or_(f'first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%,roll_number.ilike.%{search}%')
    if branch:
        query = query.eq('branch', branch)
    if semester:
        query = query.eq('semester', semester)
    
    response = query.execute()
    return {"students": response.data}

@router.get("/students/{student_id}")
async def get_student(student_id: str):
    """Get student by ID with complete profile"""
    supabase = get_supabase_admin()
    
    # Get student
    student_response = supabase.table('students').select('*').eq('id', student_id).execute()
    if not student_response.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = student_response.data[0]
    
    # Get marks
    marks_response = supabase.table('marks').select('*, subjects(name, code)').eq('student_id', student_id).execute()
    
    # Get attendance
    attendance_response = supabase.table('attendance').select('*').eq('student_id', student_id).execute()
    
    # Get fees
    fees_response = supabase.table('fees').select('*').eq('student_id', student_id).execute()
    
    return {
        "student": student,
        "marks": marks_response.data,
        "attendance": attendance_response.data,
        "fees": fees_response.data
    }

@router.post("/students")
async def create_student(student: StudentCreate):
    """Create new student"""
    supabase = get_supabase_admin()
    
    # Create auth user
    auth_response = supabase.auth.sign_up({
        "email": student.email,
        "password": student.password
    })
    
    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Failed to create user")
    
    # Create student record
    student_data = {
        "id": auth_response.user.id,
        "email": student.email,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "roll_number": student.roll_number,
        "branch": student.branch,
        "semester": student.semester,
        "phone": student.phone,
        "date_of_birth": str(student.date_of_birth) if student.date_of_birth else None
    }
    
    response = supabase.table('students').insert(student_data).execute()
    return {"student": response.data[0]}

@router.put("/students/{student_id}")
async def update_student(student_id: str, student: StudentUpdate):
    """Update student information"""
    supabase = get_supabase_admin()
    
    update_data = {k: v for k, v in student.dict().items() if v is not None}
    
    response = supabase.table('students').update(update_data).eq('id', student_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"student": response.data[0]}

@router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    """Delete student"""
    supabase = get_supabase_admin()
    
    response = supabase.table('students').delete().eq('id', student_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}


# ================== Marks Management ==================

@router.get("/marks")
async def get_all_marks(student_id: Optional[str] = None, subject_id: Optional[str] = None):
    """Get all marks with optional filters"""
    supabase = get_supabase_admin()
    
    query = supabase.table('marks').select('*, students(first_name, last_name, roll_number), subjects(name, code)')
    
    if student_id:
        query = query.eq('student_id', student_id)
    if subject_id:
        query = query.eq('subject_id', subject_id)
    
    response = query.execute()
    return {"marks": response.data}

@router.post("/marks")
async def create_mark(mark: MarkCreate):
    """Create new mark entry"""
    supabase = get_supabase_admin()
    
    mark_data = {
        "student_id": mark.student_id,
        "subject_id": mark.subject_id,
        "exam_type": mark.exam_type,
        "obtained_marks": mark.obtained_marks,
        "max_marks": mark.max_marks,
        "exam_date": str(mark.exam_date)
    }
    
    response = supabase.table('marks').insert(mark_data).execute()
    
    # Recalculate CGPA
    await recalculate_cgpa(mark.student_id)
    
    return {"mark": response.data[0]}

@router.put("/marks/{mark_id}")
async def update_mark(mark_id: str, mark: MarkUpdate):
    """Update mark entry"""
    supabase = get_supabase_admin()
    
    update_data = {k: v for k, v in mark.dict().items() if v is not None}
    if 'exam_date' in update_data:
        update_data['exam_date'] = str(update_data['exam_date'])
    
    response = supabase.table('marks').update(update_data).eq('id', mark_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Mark not found")
    
    # Recalculate CGPA
    await recalculate_cgpa(response.data[0]['student_id'])
    
    return {"mark": response.data[0]}

@router.delete("/marks/{mark_id}")
async def delete_mark(mark_id: str):
    """Delete mark entry"""
    supabase = get_supabase_admin()
    
    # Get student_id before deletion
    mark_response = supabase.table('marks').select('student_id').eq('id', mark_id).execute()
    if not mark_response.data:
        raise HTTPException(status_code=404, detail="Mark not found")
    
    student_id = mark_response.data[0]['student_id']
    
    response = supabase.table('marks').delete().eq('id', mark_id).execute()
    
    # Recalculate CGPA
    await recalculate_cgpa(student_id)
    
    return {"message": "Mark deleted successfully"}


# ================== Attendance Management ==================

@router.get("/attendance")
async def get_all_attendance(
    student_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get all attendance records with optional filters"""
    supabase = get_supabase_admin()
    
    query = supabase.table('attendance').select('*, students(first_name, last_name, roll_number), subjects(name, code)')
    
    if student_id:
        query = query.eq('student_id', student_id)
    if subject_id:
        query = query.eq('subject_id', subject_id)
    if start_date:
        query = query.gte('date', str(start_date))
    if end_date:
        query = query.lte('date', str(end_date))
    
    response = query.execute()
    return {"attendance": response.data}

@router.post("/attendance")
async def create_attendance(attendance: AttendanceCreate):
    """Create attendance record"""
    supabase = get_supabase_admin()
    
    attendance_data = {
        "student_id": attendance.student_id,
        "subject_id": attendance.subject_id,
        "date": str(attendance.date),
        "status": attendance.status
    }
    
    response = supabase.table('attendance').insert(attendance_data).execute()
    return {"attendance": response.data[0]}

@router.post("/attendance/bulk")
async def create_bulk_attendance(records: List[AttendanceCreate]):
    """Create multiple attendance records"""
    supabase = get_supabase_admin()
    
    attendance_data = [
        {
            "student_id": record.student_id,
            "subject_id": record.subject_id,
            "date": str(record.date),
            "status": record.status
        }
        for record in records
    ]
    
    response = supabase.table('attendance').insert(attendance_data).execute()
    return {"count": len(response.data), "attendance": response.data}

@router.delete("/attendance/{attendance_id}")
async def delete_attendance(attendance_id: str):
    """Delete attendance record"""
    supabase = get_supabase_admin()
    
    response = supabase.table('attendance').delete().eq('id', attendance_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    return {"message": "Attendance record deleted successfully"}


# ================== Fee Management ==================

@router.get("/fees")
async def get_all_fees(
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    semester: Optional[int] = None
):
    """Get all fee records with optional filters"""
    supabase = get_supabase_admin()
    
    query = supabase.table('fees').select('*, students(first_name, last_name, roll_number)')
    
    if student_id:
        query = query.eq('student_id', student_id)
    if status:
        query = query.eq('status', status)
    if semester:
        query = query.eq('semester', semester)
    
    response = query.execute()
    return {"fees": response.data}

@router.post("/fees")
async def create_fee(fee: FeeCreate):
    """Create fee record"""
    supabase = get_supabase_admin()
    
    fee_data = {
        "student_id": fee.student_id,
        "semester": fee.semester,
        "amount": fee.amount,
        "due_date": str(fee.due_date),
        "status": fee.status,
        "paid_amount": 0
    }
    
    response = supabase.table('fees').insert(fee_data).execute()
    return {"fee": response.data[0]}

@router.post("/fees/{fee_id}/payment")
async def record_payment(fee_id: str, payment: PaymentRecord):
    """Record fee payment"""
    supabase = get_supabase_admin()
    
    # Get current fee
    fee_response = supabase.table('fees').select('*').eq('id', fee_id).execute()
    if not fee_response.data:
        raise HTTPException(status_code=404, detail="Fee record not found")
    
    fee = fee_response.data[0]
    new_paid_amount = fee.get('paid_amount', 0) + payment.amount
    
    # Determine new status
    if new_paid_amount >= fee['amount']:
        new_status = 'paid'
    elif new_paid_amount > 0:
        new_status = 'partial'
    else:
        new_status = 'overdue'
    
    # Update fee
    update_response = supabase.table('fees').update({
        'paid_amount': new_paid_amount,
        'status': new_status
    }).eq('id', fee_id).execute()
    
    return {"fee": update_response.data[0]}

@router.delete("/fees/{fee_id}")
async def delete_fee(fee_id: str):
    """Delete fee record"""
    supabase = get_supabase_admin()
    
    response = supabase.table('fees').delete().eq('id', fee_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Fee record not found")
    
    return {"message": "Fee record deleted successfully"}


# ================== Subject Management ==================

@router.get("/subjects")
async def get_all_subjects(semester: Optional[int] = None, branch: Optional[str] = None):
    """Get all subjects with optional filters"""
    supabase = get_supabase_admin()
    
    query = supabase.table('subjects').select('*')
    
    if semester:
        query = query.eq('semester', semester)
    if branch:
        query = query.eq('branch', branch)
    
    response = query.execute()
    return {"subjects": response.data}

@router.post("/subjects")
async def create_subject(subject: SubjectCreate):
    """Create new subject"""
    supabase = get_supabase_admin()
    
    subject_data = subject.dict()
    response = supabase.table('subjects').insert(subject_data).execute()
    return {"subject": response.data[0]}

@router.put("/subjects/{subject_id}")
async def update_subject(subject_id: str, subject: SubjectCreate):
    """Update subject"""
    supabase = get_supabase_admin()
    
    response = supabase.table('subjects').update(subject.dict()).eq('id', subject_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return {"subject": response.data[0]}

@router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str):
    """Delete subject"""
    supabase = get_supabase_admin()
    
    response = supabase.table('subjects').delete().eq('id', subject_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return {"message": "Subject deleted successfully"}


# ================== Event Management ==================

@router.get("/events")
async def get_all_events(event_type: Optional[str] = None):
    """Get all events"""
    supabase = get_supabase_admin()
    
    query = supabase.table('events').select('*').order('event_date', desc=True)
    
    if event_type:
        query = query.eq('event_type', event_type)
    
    response = query.execute()
    return {"events": response.data}

@router.post("/events")
async def create_event(event: EventCreate):
    """Create new event"""
    supabase = get_supabase_admin()
    
    event_data = {
        **event.dict(),
        "event_date": event.event_date.isoformat()
    }
    
    response = supabase.table('events').insert(event_data).execute()
    return {"event": response.data[0]}

@router.put("/events/{event_id}")
async def update_event(event_id: str, event: EventCreate):
    """Update event"""
    supabase = get_supabase_admin()
    
    event_data = {
        **event.dict(),
        "event_date": event.event_date.isoformat()
    }
    
    response = supabase.table('events').update(event_data).eq('id', event_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"event": response.data[0]}

@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete event"""
    supabase = get_supabase_admin()
    
    response = supabase.table('events').delete().eq('id', event_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}


# ================== Library Management ==================

@router.get("/library/books")
async def get_all_books(category: Optional[str] = None):
    """Get all books"""
    supabase = get_supabase_admin()
    
    query = supabase.table('library_books').select('*')
    
    if category:
        query = query.eq('category', category)
    
    response = query.execute()
    return {"books": response.data}

@router.post("/library/books")
async def create_book(book: BookCreate):
    """Create new book"""
    supabase = get_supabase_admin()
    
    book_data = {**book.dict(), "available_quantity": book.quantity}
    response = supabase.table('library_books').insert(book_data).execute()
    return {"book": response.data[0]}

@router.put("/library/books/{book_id}")
async def update_book(book_id: str, book: BookCreate):
    """Update book"""
    supabase = get_supabase_admin()
    
    response = supabase.table('library_books').update(book.dict()).eq('id', book_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"book": response.data[0]}

@router.delete("/library/books/{book_id}")
async def delete_book(book_id: str):
    """Delete book"""
    supabase = get_supabase_admin()
    
    response = supabase.table('library_books').delete().eq('id', book_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book deleted successfully"}

@router.get("/library/loans")
async def get_all_loans(student_id: Optional[str] = None, status: Optional[str] = None):
    """Get all book loans"""
    supabase = get_supabase_admin()
    
    query = supabase.table('library_loans').select('*, students(first_name, last_name, roll_number), library_books(title, author)')
    
    if student_id:
        query = query.eq('student_id', student_id)
    if status:
        query = query.eq('status', status)
    
    response = query.execute()
    return {"loans": response.data}

@router.post("/library/loans")
async def create_loan(loan: LoanCreate):
    """Create book loan"""
    supabase = get_supabase_admin()
    
    # Check book availability
    book_response = supabase.table('library_books').select('*').eq('id', loan.book_id).execute()
    if not book_response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book = book_response.data[0]
    if book.get('available_quantity', 0) <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    
    # Create loan
    loan_data = {
        "student_id": loan.student_id,
        "book_id": loan.book_id,
        "issue_date": str(date.today()),
        "due_date": str(loan.due_date),
        "status": "issued"
    }
    
    loan_response = supabase.table('library_loans').insert(loan_data).execute()
    
    # Update book availability
    supabase.table('library_books').update({
        'available_quantity': book['available_quantity'] - 1
    }).eq('id', loan.book_id).execute()
    
    return {"loan": loan_response.data[0]}


# ================== Analytics ==================

@router.get("/analytics/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    supabase = get_supabase_admin()
    
    # Total students
    students_response = supabase.table('students').select('*', count='exact').execute()
    total_students = students_response.count
    
    # Average CGPA
    students_data = supabase.table('students').select('cgpa').execute()
    cgpa_values = [s.get('cgpa', 0) for s in students_data.data if s.get('cgpa')]
    avg_cgpa = sum(cgpa_values) / len(cgpa_values) if cgpa_values else 0
    
    # Attendance rate - check if attendance table exists
    try:
        attendance_response = supabase.table('attendance').select('status').execute()
        total_attendance = len(attendance_response.data)
        present_count = sum(1 for a in attendance_response.data if a['status'] == 'present')
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    except:
        attendance_rate = 0
    
    # Fee collection - using correct column names
    try:
        fees_response = supabase.table('fees').select('total_amount, paid_amount').execute()
        total_fees = sum(f['total_amount'] for f in fees_response.data)
        collected_fees = sum(f.get('paid_amount', 0) for f in fees_response.data)
        collection_rate = (collected_fees / total_fees * 100) if total_fees > 0 else 0
    except:
        total_fees = 0
        collected_fees = 0
        collection_rate = 0
    
    return {
        "total_students": total_students,
        "average_cgpa": round(avg_cgpa, 2),
        "attendance_rate": round(attendance_rate, 2),
        "fee_collection_rate": round(collection_rate, 2),
        "total_fees": total_fees,
        "collected_fees": collected_fees
    }

@router.get("/analytics/performance")
async def get_student_performance():
    """Get student performance analytics"""
    supabase = get_supabase_admin()
    
    students_response = supabase.table('students').select('department, cgpa').execute()
    
    # Group by department (not branch!)
    department_performance = {}
    for student in students_response.data:
        dept = student.get('department', 'Unknown')
        cgpa = student.get('cgpa', 0)
        
        if dept not in department_performance:
            department_performance[dept] = []
        
        if cgpa:
            department_performance[dept].append(cgpa)
    
    # Calculate averages
    performance = []
    for dept, cgpas in department_performance.items():
        avg_cgpa = sum(cgpas) / len(cgpas) if cgpas else 0
        performance.append({
            "department": dept,
            "average_cgpa": round(avg_cgpa, 2),
            "student_count": len(cgpas)
        })
    
    return {"performance": performance}

@router.get("/analytics/attendance-trends")
async def get_attendance_trends():
    """Get attendance trends"""
    supabase = get_supabase_admin()
    
    attendance_response = supabase.table('attendance').select('date, status').execute()
    
    # Group by month
    from collections import defaultdict
    monthly_trends = defaultdict(lambda: {"total": 0, "present": 0})
    
    for record in attendance_response.data:
        month = record['date'][:7]  # YYYY-MM
        monthly_trends[month]["total"] += 1
        if record['status'] == 'present':
            monthly_trends[month]["present"] += 1
    
    # Calculate percentages
    result = []
    for month, data in sorted(monthly_trends.items()):
        percentage = (data["present"] / data["total"] * 100) if data["total"] > 0 else 0
        result.append({
            "month": month,
            "attendance_percentage": round(percentage, 2),
            "total_records": data["total"]
        })
    
    return {"trends": result}

@router.get("/analytics/fee-collection")
async def get_fee_collection():
    """Get fee collection analytics"""
    supabase = get_supabase_admin()
    
    try:
        fees_response = supabase.table('fees').select('semester, total_amount, paid_amount').execute()
        
        # Group by semester
        semester_fees = {}
        for fee in fees_response.data:
            sem = fee.get('semester', 0)
            total = fee.get('total_amount', 0)
            paid = fee.get('paid_amount', 0)
            
            if sem not in semester_fees:
                semester_fees[sem] = {'total': 0, 'collected': 0}
            
            semester_fees[sem]['total'] += total
            semester_fees[sem]['collected'] += paid
        
        # Format response
        collection = []
        for sem, amounts in sorted(semester_fees.items()):
            collection.append({
                "semester": f"Sem {sem}",
                "total": amounts['total'],
                "collected": amounts['collected'],
                "collection_rate": (amounts['collected'] / amounts['total'] * 100) if amounts['total'] > 0 else 0
            })
        
        return {"collection": collection}
    except Exception as e:
        # Return empty if fees table doesn't exist or has no data
        return {"collection": []}
    
    # Group by semester
    from collections import defaultdict
    semester_collection = defaultdict(lambda: {"total": 0, "collected": 0, "pending": 0})
    
    for fee in fees_response.data:
        semester = fee['semester']
        semester_collection[semester]["total"] += fee['amount']
        semester_collection[semester]["collected"] += fee.get('paid_amount', 0)
        semester_collection[semester]["pending"] += fee['amount'] - fee.get('paid_amount', 0)
    
    # Format result
    result = []
    for semester, data in sorted(semester_collection.items()):
        collection_rate = (data["collected"] / data["total"] * 100) if data["total"] > 0 else 0
        result.append({
            "semester": semester,
            "total_fees": data["total"],
            "collected": data["collected"],
            "pending": data["pending"],
            "collection_rate": round(collection_rate, 2)
        })
    
    return {"collection": result}


# ================== Helper Functions ==================

async def recalculate_cgpa(student_id: str):
    """Recalculate and update student CGPA"""
    supabase = get_supabase_admin()
    
    # Get all marks for student
    marks_response = supabase.table('marks').select('obtained_marks, max_marks').eq('student_id', student_id).execute()
    
    if not marks_response.data:
        return
    
    # Calculate CGPA
    total_percentage = 0
    count = 0
    
    for mark in marks_response.data:
        percentage = (mark['obtained_marks'] / mark['max_marks']) * 100
        total_percentage += percentage
        count += 1
    
    avg_percentage = total_percentage / count if count > 0 else 0
    cgpa = (avg_percentage / 100) * 10  # Convert to 10-point scale
    
    # Update student CGPA
    supabase.table('students').update({'cgpa': round(cgpa, 2)}).eq('id', student_id).execute()
