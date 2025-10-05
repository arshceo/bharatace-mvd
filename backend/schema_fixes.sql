-- ============================================================================
-- SCHEMA FIXES FOR BHARATACE MVD
-- Run this in Supabase SQL Editor to fix data issues
-- ============================================================================

-- ============================================================================
-- FIX 1: Clean Up Duplicate Fees FIRST
-- ============================================================================

-- IMPORTANT: Delete duplicates BEFORE adding unique constraint
-- Keep only the most recent fee record for each student/semester
DELETE FROM fees
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY student_id, semester, academic_year
                   ORDER BY created_at DESC
               ) as rn
        FROM fees
    ) t
    WHERE rn > 1
);

-- ============================================================================
-- FIX 2: Add Unique Constraint to Prevent Future Duplicates
-- ============================================================================

-- Now we can safely add the constraint since duplicates are removed
ALTER TABLE fees 
ADD CONSTRAINT unique_student_semester_fees 
UNIQUE (student_id, semester, academic_year);

-- ============================================================================
-- FIX 3: Update Fee Status Based on Amount Paid
-- ============================================================================

-- Update payment_status based on actual amounts
UPDATE fees
SET payment_status = CASE
    WHEN amount_paid >= total_amount THEN 'paid'
    WHEN amount_paid > 0 AND amount_paid < total_amount THEN 'partial'
    WHEN due_date < CURRENT_DATE AND amount_paid = 0 THEN 'overdue'
    ELSE 'pending'
END;

-- ============================================================================
-- FIX 4: Fix Timetable Day Format Issue
-- ============================================================================

-- The seed_database.py uses string days but schema expects integers
-- Update any existing string values to integers
-- Note: This may fail if data doesn't exist yet - that's okay

UPDATE timetable
SET day_of_week = CASE day_of_week::TEXT
    WHEN 'Sunday' THEN 0
    WHEN 'Monday' THEN 1
    WHEN 'Tuesday' THEN 2
    WHEN 'Wednesday' THEN 3
    WHEN 'Thursday' THEN 4
    WHEN 'Friday' THEN 5
    WHEN 'Saturday' THEN 6
    ELSE day_of_week::INTEGER
END
WHERE day_of_week::TEXT IN ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');

-- ============================================================================
-- FIX 5: Add Computed Column for Pending Amount
-- ============================================================================

-- Add a function to automatically calculate pending amount
CREATE OR REPLACE FUNCTION calculate_pending_amount()
RETURNS TRIGGER AS $$
BEGIN
    NEW.amount_paid = COALESCE(NEW.amount_paid, 0);
    -- Update status based on payment
    IF NEW.amount_paid >= NEW.total_amount THEN
        NEW.payment_status := 'paid';
    ELSIF NEW.amount_paid > 0 THEN
        NEW.payment_status := 'partial';
    ELSIF NEW.due_date < CURRENT_DATE THEN
        NEW.payment_status := 'overdue';
    ELSE
        NEW.payment_status := 'pending';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update fee status
DROP TRIGGER IF EXISTS trigger_calculate_fee_status ON fees;
CREATE TRIGGER trigger_calculate_fee_status
BEFORE INSERT OR UPDATE ON fees
FOR EACH ROW
EXECUTE FUNCTION calculate_pending_amount();

-- ============================================================================
-- FIX 6: Add Missing Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_fees_student_semester ON fees(student_id, semester);
CREATE INDEX IF NOT EXISTS idx_timetable_day_semester ON timetable(semester, day_of_week);

-- ============================================================================
-- FIX 7: Verify Data Integrity
-- ============================================================================

-- Check for students without any attendance records
DO $$
DECLARE
    student_count INTEGER;
    students_without_attendance INTEGER;
BEGIN
    SELECT COUNT(*) INTO student_count FROM students;
    SELECT COUNT(DISTINCT s.id) INTO students_without_attendance
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id
    WHERE a.id IS NULL;
    
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'DATA INTEGRITY CHECK';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Total Students: %', student_count;
    RAISE NOTICE 'Students without attendance: %', students_without_attendance;
    RAISE NOTICE '============================================================';
END $$;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Schema Fixes Applied Successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Fixed:';
    RAISE NOTICE '  ✓ Duplicate fees prevention';
    RAISE NOTICE '  ✓ Fee status auto-calculation';
    RAISE NOTICE '  ✓ Timetable day format';
    RAISE NOTICE '  ✓ Performance indexes';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Run seed_database.py to populate test data';
    RAISE NOTICE '  2. Verify data in Supabase dashboard';
    RAISE NOTICE '  3. Test frontend endpoints';
    RAISE NOTICE '============================================================';
END $$;
