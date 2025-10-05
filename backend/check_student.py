from database import get_supabase

supabase = get_supabase()

student_id = "7e749a03-042b-48f3-a768-412e66a0e7f0"

# Get student info
student_result = supabase.table('students').select('*').eq('id', student_id).execute()
if student_result.data:
    student = student_result.data[0]
    print(f"\n{'='*60}")
    print(f"Student: {student['full_name']}")
    print(f"Email: {student['email']}")
    print(f"Roll: {student['roll_number']}")
    print(f"CGPA in students table: {student['cgpa']}")
    print(f"{'='*60}\n")

# Get marks count
marks_result = supabase.table('marks').select('*').eq('student_id', student_id).execute()
print(f"Marks records found: {len(marks_result.data)}")

if marks_result.data:
    print("\nFirst 3 marks:")
    for mark in marks_result.data[:3]:
        print(f"  - Subject ID: {mark['subject_id']}, Score: {mark['score']}")
else:
    print("\n⚠️  NO MARKS DATA FOUND!")
    print("This student doesn't have any marks in the database.")
    print("\nChecking all students with marks...")
    
    # Check which students have marks
    all_marks = supabase.table('marks').select('student_id').execute()
    unique_students = set(m['student_id'] for m in all_marks.data)
    print(f"Students with marks: {len(unique_students)}")
    
    for sid in unique_students:
        student_result = supabase.table('students').select('full_name, email').eq('id', sid).execute()
        if student_result.data:
            print(f"  - {student_result.data[0]['full_name']} ({student_result.data[0]['email']})")
