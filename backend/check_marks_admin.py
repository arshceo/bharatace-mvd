from supabase import create_client
from settings import settings

# Use SERVICE_ROLE_KEY to bypass RLS
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

student_id = "7e749a03-042b-48f3-a768-412e66a0e7f0"

print("Checking with SERVICE_ROLE_KEY (bypasses RLS)...")

# Get all marks
all_marks = supabase.table('marks').select('*').execute()
print(f"\nTotal marks records: {len(all_marks.data)}")

# Get marks for specific student
student_marks = supabase.table('marks').select('*').eq('student_id', student_id).execute()
print(f"Marks for student {student_id}: {len(student_marks.data)}")

if student_marks.data:
    print("\nFirst 3 marks:")
    for mark in student_marks.data[:3]:
        print(f"  Mark data: {mark}")
else:
    print("\n⚠️  Still no marks found even with SERVICE_ROLE_KEY!")
    print("Checking all students in marks table...")
    unique_students = set(m['student_id'] for m in all_marks.data)
    print(f"Unique students with marks: {len(unique_students)}")
    for sid in list(unique_students)[:5]:
        print(f"  - {sid}")
