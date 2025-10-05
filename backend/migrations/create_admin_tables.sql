"""
Database schema for admin tables
Run this SQL in Supabase SQL Editor
"""

-- Admin Users Table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'institution_admin',
    permissions JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Faculty Table
CREATE TABLE IF NOT EXISTS faculty (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    department_id UUID REFERENCES departments(id),
    designation VARCHAR(100),
    qualification VARCHAR(255),
    experience_years INTEGER DEFAULT 0,
    date_of_joining DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Faculty Subject Assignments
CREATE TABLE IF NOT EXISTS faculty_subject_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id UUID REFERENCES faculty(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    academic_year VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(faculty_id, subject_id, semester, academic_year)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_admin_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_institution ON admin_users(institution_id);
CREATE INDEX IF NOT EXISTS idx_faculty_email ON faculty(email);
CREATE INDEX IF NOT EXISTS idx_faculty_department ON faculty(department_id);
CREATE INDEX IF NOT EXISTS idx_faculty_assignments ON faculty_subject_assignments(faculty_id, subject_id);

-- Insert demo super admin (password: admin123)
INSERT INTO admin_users (email, password_hash, full_name, role, permissions) VALUES
('admin@bharatace.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQx.eLSSC', 'Super Admin', 'super_admin', 
'{"can_manage_institutions": true, "can_manage_students": true, "can_manage_faculty": true, "can_enter_marks": true, "can_mark_attendance": true, "can_manage_fees": true, "can_manage_library": true, "can_manage_events": true, "can_manage_knowledge_base": true, "can_view_reports": true, "can_export_data": true, "can_delete_records": true}'::jsonb)
ON CONFLICT (email) DO NOTHING;

COMMENT ON TABLE admin_users IS 'Admin users with role-based permissions';
COMMENT ON TABLE faculty IS 'Faculty/teacher information';
COMMENT ON TABLE faculty_subject_assignments IS 'Maps faculty to subjects they teach';
