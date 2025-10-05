"""
Database Seeding Script
Populates the database with realistic demo data for testing.

Creates:
- 1 Default Institution
- 4 Demo Students with complete profiles
- Attendance records (realistic percentages)
- Marks records (various subjects and exams)
- Fee records (some paid, some pending)
- Library books and loans
- Events and registrations
- Timetable entries
- Subjects
"""

import uuid
from datetime import datetime, timedelta, date
import random
from database import get_supabase
from auth import hash_password
from settings import settings
from supabase import create_client

def seed_database():
    """Main seeding function"""
    print("=" * 80)
    print("🌱 SEEDING DATABASE WITH DEMO DATA")
    print("=" * 80)
    
    # Use service role key if available (bypasses RLS for admin operations)
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        print("ℹ️  Using SERVICE ROLE key (bypasses RLS)")
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    else:
        print("⚠️  Using ANON key - RLS policies will apply")
        print("   If you encounter RLS errors, add SUPABASE_SERVICE_ROLE_KEY to .env")
        supabase = get_supabase()
    
    # Clear existing demo data (optional - comment out to preserve data)
    # print("\n🧹 Clearing existing demo data...")
    # clear_demo_data(supabase)
    
    # Create institution
    print("\n🏛️  Creating institution...")
    institution_id = create_institution(supabase)
    
    # Create subjects
    print("\n📚 Creating subjects...")
    subjects = create_subjects(supabase, institution_id)
    
    # Create demo students
    print("\n👥 Creating demo students...")
    students = create_students(supabase, institution_id)
    
    # Create attendance records
    print("\n📝 Creating attendance records...")
    # Check if attendance already exists
    existing_attendance = supabase.table("attendance").select("id").limit(1).execute()
    if existing_attendance.data:
        print("   ↻ Attendance records already exist, skipping...")
    else:
        create_attendance(supabase, students, subjects)
    
    # Create marks records
    print("\n🎯 Creating marks records...")
    create_marks(supabase, students, subjects)
    
    # Create fee records
    print("\n💰 Creating fee records...")
    create_fees(supabase, students)
    
    # Create library books
    print("\n📖 Creating library books...")
    existing_books = supabase.table("library_books").select("id").limit(1).execute()
    if existing_books.data:
        print("   ↻ Library books already exist, fetching existing books...")
        books = supabase.table("library_books").select("*").execute().data
    else:
        books = create_library_books(supabase, institution_id)
    
    # Create book loans
    print("\n📚 Creating book loans...")
    existing_loans = supabase.table("book_loans").select("id").limit(1).execute()
    if existing_loans.data:
        print("   ↻ Book loans already exist, skipping...")
    else:
        create_book_loans(supabase, students, books)
    
    # Create events
    print("\n🎉 Creating events...")
    existing_events = supabase.table("events").select("id").limit(1).execute()
    if existing_events.data:
        print("   ↻ Events already exist, fetching existing events...")
        events = supabase.table("events").select("*").execute().data
    else:
        events = create_events(supabase, institution_id)
    
    # Create event registrations
    print("\n✍️  Creating event registrations...")
    existing_participation = supabase.table("event_participation").select("id").limit(1).execute()
    if existing_participation.data:
        print("   ↻ Event registrations already exist, skipping...")
    else:
        create_event_registrations(supabase, students, events)
    
    # Create timetable
    print("\n🕐 Creating timetable...")
    existing_timetable = supabase.table("timetable").select("id").limit(1).execute()
    if existing_timetable.data:
        print("   ↻ Timetable already exists, skipping...")
    else:
        create_timetable(supabase, institution_id, subjects)
    
    print("\n" + "=" * 80)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("=" * 80)
    print("\n📋 Demo Student Accounts:")
    print("-" * 80)
    for student in students:
        print(f"\n📧 Email: {student['email']}")
        print(f"🔑 Password: password123")
        print(f"👤 Name: {student['full_name']}")
        print(f"🎓 Roll: {student['roll_number']} | Sem: {student['semester']} | Dept: {student['department']}")
    print("-" * 80)


def create_institution(supabase):
    """Create default institution"""
    # Check if institution already exists
    existing = supabase.table("institutions").select("*").eq("code", "BACE2023").execute()
    
    if existing.data:
        print(f"   ✓ Using existing: {existing.data[0]['name']}")
        return existing.data[0]['id']
    
    institution_id = str(uuid.uuid4())
    
    data = {
        "id": institution_id,
        "name": "BharatAce College of Engineering",
        "code": "BACE2023",
        "address": "123, MG Road, Bangalore, Karnataka - 560001",
        "email": "info@bharatace.edu.in",
        "phone": "+91 80 1234 5678",
        "logo_url": "https://bharatace.edu.in/logo.png"
    }
    
    supabase.table("institutions").insert(data).execute()
    print(f"   ✓ Created: {data['name']}")
    
    return institution_id


def create_subjects(supabase, institution_id):
    """Create subjects for different semesters"""
    subjects_data = [
        # Semester 3
        {"subject_name": "Data Structures", "subject_code": "CS301", "semester": 3, "credits": 4, "department": "Computer Science", "instructor_name": "Dr. Sharma"},
        {"subject_name": "Database Management Systems", "subject_code": "CS302", "semester": 3, "credits": 4, "department": "Computer Science", "instructor_name": "Prof. Kumar"},
        {"subject_name": "Operating Systems", "subject_code": "CS303", "semester": 3, "credits": 3, "department": "Computer Science", "instructor_name": "Dr. Patel"},
        {"subject_name": "Computer Networks", "subject_code": "CS304", "semester": 3, "credits": 3, "department": "Computer Science", "instructor_name": "Prof. Singh"},
        
        # Semester 5
        {"subject_name": "Design and Analysis of Algorithms", "subject_code": "CS501", "semester": 5, "credits": 4, "department": "Computer Science", "instructor_name": "Dr. Sharma"},
        {"subject_name": "Software Engineering", "subject_code": "CS502", "semester": 5, "credits": 3, "department": "Computer Science", "instructor_name": "Prof. Mehta"},
        {"subject_name": "Machine Learning", "subject_code": "CS503", "semester": 5, "credits": 4, "department": "Computer Science", "instructor_name": "Dr. Gupta"},
        {"subject_name": "Web Technologies", "subject_code": "CS504", "semester": 5, "credits": 3, "department": "Computer Science", "instructor_name": "Prof. Kumar"},
        
        # Semester 6
        {"subject_name": "Artificial Intelligence", "subject_code": "EC601", "semester": 6, "credits": 4, "department": "Electronics", "instructor_name": "Dr. Rao"},
        {"subject_name": "Cloud Computing", "subject_code": "EC602", "semester": 6, "credits": 3, "department": "Electronics", "instructor_name": "Prof. Iyer"},
        
        # Semester 7
        {"subject_name": "Deep Learning", "subject_code": "IT701", "semester": 7, "credits": 4, "department": "Information Technology", "instructor_name": "Dr. Verma"},
        {"subject_name": "Blockchain Technology", "subject_code": "IT702", "semester": 7, "credits": 3, "department": "Information Technology", "instructor_name": "Prof. Joshi"},
    ]
    
    subjects = []
    for subj in subjects_data:
        # Check if subject already exists
        existing = supabase.table("subjects")\
            .select("*")\
            .eq("subject_code", subj['subject_code'])\
            .execute()
        
        if existing.data:
            subjects.append(existing.data[0])
            print(f"   ↻ {subj['subject_code']}: {subj['subject_name']} (already exists)")
        else:
            subject_id = str(uuid.uuid4())
            data = {
                "id": subject_id,
                "institution_id": institution_id,
                **subj
            }
            result = supabase.table("subjects").insert(data).execute()
            subjects.append(result.data[0])
            print(f"   ✓ {subj['subject_code']}: {subj['subject_name']}")
    
    return subjects


def create_students(supabase, institution_id):
    """Create 4 demo students with varied profiles"""
    password_hash = hash_password("password123")
    
    students_data = [
        {
            "full_name": "Priya Sharma",
            "roll_number": "CS2021001",
            "email": "priya.sharma@bharatace.edu.in",
            "semester": 5,
            "department": "Computer Science",
            "phone": "+91 98765 43210",
            "admission_year": 2021,
            "cgpa": 8.2,
            "course": "B.Tech Computer Science"
        },
        {
            "full_name": "Amit Kumar",
            "roll_number": "EC2020015",
            "email": "amit.kumar@bharatace.edu.in",
            "semester": 6,
            "department": "Electronics",
            "phone": "+91 98765 43211",
            "admission_year": 2020,
            "cgpa": 7.8,
            "course": "B.Tech Electronics"
        },
        {
            "full_name": "Sneha Patel",
            "roll_number": "CS2022042",
            "email": "sneha.patel@bharatace.edu.in",
            "semester": 3,
            "department": "Computer Science",
            "phone": "+91 98765 43212",
            "admission_year": 2022,
            "cgpa": 8.9,
            "course": "B.Tech Computer Science"
        },
        {
            "full_name": "Rahul Singh",
            "roll_number": "IT2019023",
            "email": "rahul.singh@bharatace.edu.in",
            "semester": 7,
            "department": "Information Technology",
            "phone": "+91 98765 43213",
            "admission_year": 2019,
            "cgpa": 7.2,
            "course": "B.Tech Information Technology"
        },
    ]
    
    students = []
    for student in students_data:
        # Check if student already exists
        existing = supabase.table("students")\
            .select("*")\
            .eq("email", student['email'])\
            .execute()
        
        if existing.data:
            students.append(existing.data[0])
            print(f"   ↻ {student['full_name']} ({student['roll_number']}) - already exists")
        else:
            student_id = str(uuid.uuid4())
            data = {
                "id": student_id,
                "institution_id": institution_id,
                "password_hash": password_hash,
                **student
            }
            result = supabase.table("students").insert(data).execute()
            students.append(result.data[0])
            print(f"   ✓ {student['full_name']} ({student['roll_number']})")
    
    return students


def create_attendance(supabase, students, subjects):
    """Create realistic attendance records"""
    # Define target percentages for each student
    attendance_targets = [79.2, 82.5, 88.3, 71.5]  # Priya, Amit, Sneha, Rahul
    
    for idx, student in enumerate(students):
        student_subjects = [s for s in subjects if s['semester'] == student['semester']]
        target = attendance_targets[idx]
        
        for subject in student_subjects:
            total_classes = random.randint(40, 60)
            attended = int(total_classes * target / 100)
            
            # Generate attendance records for the past 2 months
            start_date = datetime.now() - timedelta(days=60)
            
            for i in range(total_classes):
                attendance_date = start_date + timedelta(days=i)
                
                # Skip weekends
                if attendance_date.weekday() >= 5:
                    continue
                
                # Determine status based on target
                rand = random.random() * 100
                if rand < target:
                    status = "present" if rand < (target - 5) else "late"
                else:
                    status = "absent"
                
                attendance_id = str(uuid.uuid4())
                data = {
                    "id": attendance_id,
                    "student_id": student['id'],
                    "subject_id": subject['id'],
                    "date": attendance_date.date().isoformat(),
                    "status": status
                }
                
                supabase.table("attendance").insert(data).execute()
            
            print(f"   ✓ {student['full_name']}: {subject['subject_name']} - {attended}/{total_classes} ({target}%)")


def create_marks(supabase, students, subjects):
    """Create marks records for various exams"""
    exam_types = ["midterm", "final", "quiz", "assignment"]
    
    for student in students:
        student_subjects = [s for s in subjects if s['semester'] == student['semester']]
        
        for subject in student_subjects:
            for exam_type in exam_types:
                # Generate marks based on CGPA
                cgpa = student['cgpa']
                base_percentage = (cgpa / 10) * 100
                
                # Add randomness
                variation = random.uniform(-10, 10)
                percentage = max(40, min(95, base_percentage + variation))
                
                # Calculate marks
                max_marks = 100 if exam_type in ["midterm", "final"] else (20 if exam_type == "quiz" else 10)
                marks_obtained = (percentage / 100) * max_marks
                
                exam_date = datetime.now() - timedelta(days=random.randint(7, 60))
                
                mark_id = str(uuid.uuid4())
                data = {
                    "id": mark_id,
                    "student_id": student['id'],
                    "subject_id": subject['id'],
                    "exam_type": exam_type,
                    "obtained_marks": round(marks_obtained, 2),
                    "max_marks": max_marks,
                    "exam_date": exam_date.date().isoformat()
                }
                
                supabase.table("marks").insert(data).execute()
        
        print(f"   ✓ {student['full_name']}: {len(student_subjects) * len(exam_types)} exam records")


def create_fees(supabase, students):
    """Create fee records with varied payment statuses"""
    fee_statuses = [
        {"total": 50000, "paid": 48000, "status": "partial"},  # Priya
        {"total": 50000, "paid": 50000, "status": "paid"},     # Amit
        {"total": 50000, "paid": 45000, "status": "partial"},  # Sneha
        {"total": 50000, "paid": 35000, "status": "overdue"},  # Rahul
    ]
    
    for idx, student in enumerate(students):
        fee_config = fee_statuses[idx]
        
        # Create fee record
        fee_id = str(uuid.uuid4())
        due_date = datetime.now() - timedelta(days=15) if fee_config["status"] == "overdue" else datetime.now() + timedelta(days=15)
        
        late_fee = 0
        if fee_config["status"] == "overdue":
            days_overdue = 20
            late_fee = min(days_overdue * 200, fee_config["total"] * 0.2)  # ₹200/day, capped at 20%
        
        data = {
            "id": fee_id,
            "student_id": student['id'],
            "semester": student['semester'],
            "academic_year": "2024-2025",
            "total_amount": fee_config["total"],
            "amount_paid": fee_config["paid"],
            "due_date": due_date.date().isoformat(),
            "payment_status": fee_config["status"],
            "late_fee": late_fee
        }
        
        supabase.table("fees").insert(data).execute()
        
        # Create payment transaction if paid
        if fee_config["paid"] > 0:
            transaction_id_str = str(uuid.uuid4())
            transaction_data = {
                "id": transaction_id_str,
                "fee_id": fee_id,
                "student_id": student['id'],
                "amount": fee_config["paid"],
                "payment_method": random.choice(["upi", "card", "netbanking"]),
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "transaction_date": (datetime.now() - timedelta(days=random.randint(5, 30))).isoformat(),
                "payment_status": "success"
            }
            supabase.table("fee_transactions").insert(transaction_data).execute()
        
        print(f"   ✓ {student['full_name']}: ₹{fee_config['paid']}/₹{fee_config['total']} ({fee_config['status']})")


def create_library_books(supabase, institution_id):
    """Create library book catalog"""
    books_data = [
        {"title": "Introduction to Algorithms", "author": "Cormen, Leiserson, Rivest, Stein", "isbn": "978-0262033848", "category": "Computer Science", "total_copies": 5, "available_copies": 3, "publisher": "MIT Press", "publication_year": 2009},
        {"title": "Database System Concepts", "author": "Silberschatz, Korth, Sudarshan", "isbn": "978-0078022159", "category": "Computer Science", "total_copies": 4, "available_copies": 2, "publisher": "McGraw Hill", "publication_year": 2010},
        {"title": "Operating System Concepts", "author": "Silberschatz, Galvin, Gagne", "isbn": "978-1118063330", "category": "Computer Science", "total_copies": 3, "available_copies": 1, "publisher": "Wiley", "publication_year": 2012},
        {"title": "Computer Networks", "author": "Andrew S. Tanenbaum", "isbn": "978-0132126953", "category": "Computer Science", "total_copies": 4, "available_copies": 3, "publisher": "Pearson", "publication_year": 2010},
        {"title": "Artificial Intelligence: A Modern Approach", "author": "Stuart Russell, Peter Norvig", "isbn": "978-0136042594", "category": "AI/ML", "total_copies": 3, "available_copies": 2, "publisher": "Pearson", "publication_year": 2020},
        {"title": "Machine Learning", "author": "Tom Mitchell", "isbn": "978-0070428072", "category": "AI/ML", "total_copies": 2, "available_copies": 0, "publisher": "McGraw Hill", "publication_year": 1997},
        {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884", "category": "Software Engineering", "total_copies": 5, "available_copies": 4, "publisher": "Prentice Hall", "publication_year": 2008},
        {"title": "Design Patterns", "author": "Gang of Four", "isbn": "978-0201633610", "category": "Software Engineering", "total_copies": 3, "available_copies": 2, "publisher": "Addison-Wesley", "publication_year": 1994},
    ]
    
    books = []
    for book in books_data:
        book_id = str(uuid.uuid4())
        data = {
            "id": book_id,
            "institution_id": institution_id,
            **book
        }
        result = supabase.table("library_books").insert(data).execute()
        books.append(result.data[0])
        print(f"   ✓ {book['title']} ({book['available_copies']}/{book['total_copies']} available)")
    
    return books


def create_book_loans(supabase, students, books):
    """Create book loan records"""
    # Priya: 2 books (1 overdue)
    # Amit: 1 book
    # Sneha: 2 books
    # Rahul: 3 books (1 overdue with fine)
    
    loans_config = [
        {"count": 2, "overdue": 1},  # Priya
        {"count": 1, "overdue": 0},  # Amit
        {"count": 2, "overdue": 0},  # Sneha
        {"count": 3, "overdue": 1},  # Rahul
    ]
    
    for idx, student in enumerate(students):
        config = loans_config[idx]
        student_books = random.sample(books, min(config["count"], len(books)))
        
        for i, book in enumerate(student_books):
            loan_id = str(uuid.uuid4())
            
            is_overdue = i < config["overdue"]
            issue_date = datetime.now() - timedelta(days=(20 if is_overdue else random.randint(1, 10)))
            due_date = issue_date + timedelta(days=14)
            
            fine_amount = 0
            loan_status = "active"
            if is_overdue:
                days_overdue = (datetime.now() - due_date).days
                fine_amount = days_overdue * 5  # ₹5/day
                loan_status = "overdue"
            
            data = {
                "id": loan_id,
                "book_id": book['id'],
                "student_id": student['id'],
                "issue_date": issue_date.isoformat(),
                "due_date": due_date.date().isoformat(),
                "return_date": None,
                "loan_status": loan_status,
                "fine_amount": fine_amount
            }
            
            supabase.table("book_loans").insert(data).execute()
        
        print(f"   ✓ {student['full_name']}: {config['count']} books issued")


def create_events(supabase, institution_id):
    """Create upcoming events"""
    events_data = [
        {
            "title": "AI & Machine Learning Workshop",
            "description": "Learn the fundamentals of AI and ML with hands-on projects",
            "event_type": "workshop",
            "start_date": (datetime.now() + timedelta(days=10)).isoformat(),
            "location": "Seminar Hall A",
            "organizer": "CS Department",
            "max_participants": 50,
            "registration_deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "event_status": "scheduled"
        },
        {
            "title": "Hackathon 2025",
            "description": "24-hour coding challenge with exciting prizes",
            "event_type": "cultural",
            "start_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=16)).isoformat(),
            "location": "Computer Lab",
            "organizer": "Tech Club",
            "max_participants": 100,
            "registration_deadline": (datetime.now() + timedelta(days=12)).isoformat(),
            "event_status": "scheduled"
        },
        {
            "title": "Career Guidance Seminar",
            "description": "Industry experts sharing career insights and opportunities",
            "event_type": "seminar",
            "start_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "location": "Auditorium",
            "organizer": "Placement Cell",
            "max_participants": 200,
            "event_status": "scheduled"
        },
        {
            "title": "Annual Tech Fest",
            "description": "3-day technology festival with competitions, workshops, and talks",
            "event_type": "fest",
            "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=33)).isoformat(),
            "location": "College Campus",
            "organizer": "Student Council",
            "max_participants": 500,
            "event_status": "scheduled"
        },
    ]
    
    events = []
    for event in events_data:
        event_id = str(uuid.uuid4())
        data = {
            "id": event_id,
            "institution_id": institution_id,
            **event
        }
        result = supabase.table("events").insert(data).execute()
        events.append(result.data[0])
        print(f"   ✓ {event['title']} ({event['event_type']})")
    
    return events


def create_event_registrations(supabase, students, events):
    """Create event registrations"""
    # Register students for various events
    for student in students:
        # Each student registers for 1-2 events
        student_events = random.sample(events, random.randint(1, 2))
        
        for event in student_events:
            registration_id = str(uuid.uuid4())
            data = {
                "id": registration_id,
                "event_id": event['id'],
                "student_id": student['id'],
                "registration_date": datetime.now().isoformat(),
                "attendance_status": "registered"
            }
            supabase.table("event_participation").insert(data).execute()
        
        print(f"   ✓ {student['full_name']}: {len(student_events)} events registered")


def create_timetable(supabase, institution_id, subjects):
    """Create weekly timetable"""
    # Time slots (9 AM - 5 PM)
    time_slots = [
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
        ("12:00", "13:00"),
        ("14:00", "15:00"),  # After lunch break
        ("15:00", "16:00"),
        ("16:00", "17:00"),
    ]
    
    # Days (1=Monday to 5=Friday)
    days = [1, 2, 3, 4, 5]
    
    # Room numbers
    rooms = ["301", "302", "303", "Lab-1", "Lab-2"]
    
    # Create timetable for each semester
    for semester in [3, 5, 6, 7]:
        semester_subjects = [s for s in subjects if s['semester'] == semester]
        
        for day in days:
            # 4-5 classes per day
            day_slots = random.sample(time_slots, random.randint(4, 5))
            
            for start_time, end_time in day_slots:
                subject = random.choice(semester_subjects)
                
                timetable_id = str(uuid.uuid4())
                data = {
                    "id": timetable_id,
                    "institution_id": institution_id,
                    "semester": semester,
                    "day_of_week": day,
                    "start_time": start_time,
                    "end_time": end_time,
                    "subject_id": subject['id'],
                    "room_number": random.choice(rooms),
                    "session_type": random.choice(["lecture", "lab", "tutorial"])
                }
                
                supabase.table("timetable").insert(data).execute()
        
        print(f"   ✓ Semester {semester}: Weekly schedule created")


if __name__ == "__main__":
    seed_database()
