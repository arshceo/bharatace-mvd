from database import get_supabase_admin
from tools.marks_tool import calculate_cgpa

supabase = get_supabase_admin()

# Get Sneha's ID and stored CGPA
student_id = "7e749a03-042b-48f3-a768-412e66a0e7f0"

student_result = supabase.table('students').select('*').eq('id', student_id).execute()
if student_result.data:
    student = student_result.data[0]
    print(f"\n{'='*70}")
    print(f"STUDENT INFO FROM DATABASE")
    print(f"{'='*70}")
    print(f"Name: {student['full_name']}")
    print(f"CGPA (stored in students table): {student['cgpa']}")
    print(f"{'='*70}\n")

# Get all marks and calculate CGPA
marks_result = supabase.table('marks').select('*, subjects(subject_name, subject_code, credits, semester)').eq('student_id', student_id).execute()

print(f"Total marks records: {len(marks_result.data)}\n")

# Calculate CGPA using the tool
print(f"{'='*70}")
print(f"CALCULATING CGPA FROM MARKS DATA")
print(f"{'='*70}")
cgpa_result = calculate_cgpa(student_id)
print(f"\nCalculated CGPA: {cgpa_result['cgpa']}")
print(f"Total Credits: {cgpa_result['total_credits']}")
print(f"\nSemester-wise breakdown:")
for sem, data in cgpa_result.get('semester_wise', {}).items():
    print(f"  Semester {sem}: GPA = {data['gpa']:.2f}, Credits = {data['credits']}")

print(f"\n{'='*70}")
print(f"DISCREPANCY FOUND!")
print(f"{'='*70}")
print(f"Stored CGPA: {student['cgpa']}")
print(f"Calculated CGPA: {cgpa_result['cgpa']}")
print(f"Difference: {abs(float(student['cgpa']) - cgpa_result['cgpa']):.2f}")
print(f"{'='*70}\n")

# Show sample marks
print("Sample marks (first 5):")
for i, mark in enumerate(marks_result.data[:5]):
    subject = mark.get('subjects', {})
    print(f"{i+1}. {subject.get('subject_name', 'Unknown')}: {mark['obtained_marks']}/{mark['max_marks']} (Sem {subject.get('semester', '?')})")
