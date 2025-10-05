-- ============================================================================
-- SIMPLE SCHEMA UPDATE FOR AUTH DEMO
-- Run this SQL in your Supabase SQL Editor to add required fields
-- ============================================================================

-- Add password_hash to students table (for custom auth without Supabase Auth)
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS password_hash TEXT,
ADD COLUMN IF NOT EXISTS roll_number VARCHAR(50) UNIQUE,
ADD COLUMN IF NOT EXISTS full_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS cgpa DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS admission_year INTEGER;

-- Add password_hash to admin_users table
ALTER TABLE admin_users 
ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_students_roll_number ON students(roll_number);
CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);

-- Make student_id nullable (since we're using roll_number instead)
ALTER TABLE students ALTER COLUMN student_id DROP NOT NULL;
ALTER TABLE students ALTER COLUMN first_name DROP NOT NULL;
ALTER TABLE students ALTER COLUMN last_name DROP NOT NULL;
ALTER TABLE students ALTER COLUMN course DROP NOT NULL;

COMMENT ON COLUMN students.password_hash IS 'Bcrypt hashed password for custom authentication';
COMMENT ON COLUMN students.roll_number IS 'Student roll number / registration number';
COMMENT ON COLUMN students.full_name IS 'Complete name of the student';
COMMENT ON COLUMN students.cgpa IS 'Cumulative Grade Point Average (0.00 to 10.00)';
