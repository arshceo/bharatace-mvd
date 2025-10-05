"""
Update students table with calculated CGPA from marks data
"""
from database import get_supabase_admin
from tools.marks_tool import calculate_cgpa

supabase = get_supabase_admin()

# Get all students
students_result = supabase.table('students').select('id, full_name, email, cgpa').execute()

print(f"\n{'='*80}")
print(f"UPDATING STUDENT CGPAs FROM MARKS DATA")
print(f"{'='*80}\n")

for student in students_result.data:
    student_id = student['id']
    old_cgpa = student['cgpa']
    
    # Calculate CGPA from marks
    cgpa_result = calculate_cgpa(student_id)
    new_cgpa = cgpa_result['cgpa']
    
    if new_cgpa > 0:  # Only update if we have marks data
        # Update in database
        supabase.table('students').update({'cgpa': new_cgpa}).eq('id', student_id).execute()
        
        print(f"✓ {student['full_name']}")
        print(f"  Old CGPA: {old_cgpa}")
        print(f"  New CGPA: {new_cgpa}")
        print(f"  Change: {new_cgpa - float(old_cgpa):+.2f}")
        print()
    else:
        print(f"⊘ {student['full_name']} - No marks data available")
        print()

print(f"{'='*80}")
print(f"✓ CGPA UPDATE COMPLETE!")
print(f"{'='*80}\n")
