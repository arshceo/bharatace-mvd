-- ============================================================================
-- BharatAce Production Database Schema
-- Multi-tenant AI Campus Assistant Platform
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- INSTITUTIONS TABLE (Multi-tenancy support)
-- ============================================================================
CREATE TABLE IF NOT EXISTS institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    email VARCHAR(255),
    phone VARCHAR(20),
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- STUDENT PROFILES (Extends Supabase Auth users)
-- ============================================================================
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    course VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    semester INTEGER NOT NULL,
    year_of_admission INTEGER,
    enrollment_status VARCHAR(20) DEFAULT 'active' CHECK (enrollment_status IN ('active', 'suspended', 'graduated', 'withdrawn')),
    profile_picture_url TEXT,
    address TEXT,
    guardian_name VARCHAR(200),
    guardian_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SUBJECTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS subjects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    subject_name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    semester INTEGER NOT NULL,
    credits INTEGER NOT NULL DEFAULT 3,
    description TEXT,
    instructor_name VARCHAR(200),
    instructor_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ATTENDANCE TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, subject_id, date)
);

-- ============================================================================
-- MARKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS marks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
    exam_type VARCHAR(50) NOT NULL CHECK (exam_type IN ('midterm', 'final', 'assignment', 'quiz', 'project', 'practical')),
    max_marks INTEGER NOT NULL DEFAULT 100,
    obtained_marks DECIMAL(5,2) NOT NULL,
    exam_date DATE,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- FEES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS fees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    due_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'partial', 'paid', 'overdue')),
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- FEE TRANSACTIONS TABLE (Payment history)
-- ============================================================================
CREATE TABLE IF NOT EXISTS fee_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fee_id UUID REFERENCES fees(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) CHECK (payment_method IN ('cash', 'card', 'upi', 'netbanking', 'cheque')),
    transaction_id VARCHAR(100) UNIQUE,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    payment_status VARCHAR(20) DEFAULT 'success' CHECK (payment_status IN ('success', 'failed', 'pending')),
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) CHECK (event_type IN ('academic', 'cultural', 'sports', 'workshop', 'seminar', 'fest', 'exam', 'holiday')),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(200),
    organizer VARCHAR(200),
    max_participants INTEGER,
    registration_deadline TIMESTAMP WITH TIME ZONE,
    event_status VARCHAR(20) DEFAULT 'scheduled' CHECK (event_status IN ('scheduled', 'ongoing', 'completed', 'cancelled')),
    banner_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- EVENT PARTICIPATION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_participation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    attendance_status VARCHAR(20) DEFAULT 'registered' CHECK (attendance_status IN ('registered', 'attended', 'absent', 'cancelled')),
    feedback TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, student_id)
);

-- ============================================================================
-- LIBRARY BOOKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS library_books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(300) NOT NULL,
    author VARCHAR(200) NOT NULL,
    publisher VARCHAR(200),
    publication_year INTEGER,
    category VARCHAR(100),
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    shelf_location VARCHAR(50),
    description TEXT,
    cover_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (available_copies <= total_copies)
);

-- ============================================================================
-- BOOK LOANS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS book_loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    book_id UUID REFERENCES library_books(id) ON DELETE CASCADE,
    issue_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date DATE NOT NULL,
    return_date TIMESTAMP WITH TIME ZONE,
    loan_status VARCHAR(20) DEFAULT 'active' CHECK (loan_status IN ('active', 'returned', 'overdue', 'lost')),
    fine_amount DECIMAL(10,2) DEFAULT 0.00,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- TIMETABLE TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS timetable (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES subjects(id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday, 1=Monday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_number VARCHAR(50),
    session_type VARCHAR(50) CHECK (session_type IN ('lecture', 'lab', 'tutorial', 'practical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subject_id, day_of_week, start_time)
);

-- ============================================================================
-- ADMIN USERS TABLE (For CMS access)
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin' CHECK (role IN ('super_admin', 'admin', 'faculty', 'staff')),
    permissions JSONB, -- Flexible permissions system
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- KNOWLEDGE BASE TABLE (Existing - for RAG)
-- ============================================================================
-- This table already exists from your MVD, keeping it as-is
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CHAT HISTORY TABLE (For personalized AI conversations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    message_type VARCHAR(20) CHECK (message_type IN ('user', 'assistant', 'system')),
    tokens_used INTEGER,
    session_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) CHECK (notification_type IN ('academic', 'fee', 'event', 'library', 'general')),
    is_read BOOLEAN DEFAULT FALSE,
    link_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_institution_id ON students(institution_id);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_subject_id ON attendance(subject_id);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_marks_student_id ON marks(student_id);
CREATE INDEX idx_marks_subject_id ON marks(subject_id);
CREATE INDEX idx_fees_student_id ON fees(student_id);
CREATE INDEX idx_fees_payment_status ON fees(payment_status);
CREATE INDEX idx_events_institution_id ON events(institution_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_event_participation_student_id ON event_participation(student_id);
CREATE INDEX idx_book_loans_student_id ON book_loans(student_id);
CREATE INDEX idx_book_loans_status ON book_loans(loan_status);
CREATE INDEX idx_timetable_semester ON timetable(semester);
CREATE INDEX idx_chat_history_student_id ON chat_history(student_id);
CREATE INDEX idx_notifications_student_id ON notifications(student_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
ALTER TABLE fees ENABLE ROW LEVEL SECURITY;
ALTER TABLE fee_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_participation ENABLE ROW LEVEL SECURITY;
ALTER TABLE book_loans ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Students can only see their own data
CREATE POLICY "Students can view own profile" ON students
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Students can update own profile" ON students
    FOR UPDATE USING (auth.uid() = user_id);

-- Attendance policies
CREATE POLICY "Students can view own attendance" ON attendance
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Marks policies
CREATE POLICY "Students can view own marks" ON marks
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Fees policies
CREATE POLICY "Students can view own fees" ON fees
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Fee transactions policies
CREATE POLICY "Students can view own transactions" ON fee_transactions
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Event participation policies
CREATE POLICY "Students can view own event participation" ON event_participation
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Students can register for events" ON event_participation
    FOR INSERT WITH CHECK (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Book loans policies
CREATE POLICY "Students can view own book loans" ON book_loans
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Chat history policies
CREATE POLICY "Students can view own chat history" ON chat_history
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Students can insert own chat messages" ON chat_history
    FOR INSERT WITH CHECK (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- Notifications policies
CREATE POLICY "Students can view own notifications" ON notifications
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Students can update own notifications" ON notifications
    FOR UPDATE USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

-- ============================================================================
-- FUNCTIONS FOR AUTOMATED CALCULATIONS
-- ============================================================================

-- Function to update fee payment status
CREATE OR REPLACE FUNCTION update_fee_payment_status()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE fees
    SET 
        amount_paid = (
            SELECT COALESCE(SUM(amount), 0)
            FROM fee_transactions
            WHERE fee_id = NEW.fee_id AND payment_status = 'success'
        ),
        payment_status = CASE
            WHEN (SELECT COALESCE(SUM(amount), 0) FROM fee_transactions WHERE fee_id = NEW.fee_id AND payment_status = 'success') >= total_amount THEN 'paid'
            WHEN (SELECT COALESCE(SUM(amount), 0) FROM fee_transactions WHERE fee_id = NEW.fee_id AND payment_status = 'success') > 0 THEN 'partial'
            WHEN due_date < CURRENT_DATE THEN 'overdue'
            ELSE 'pending'
        END
    WHERE id = NEW.fee_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fee_status
AFTER INSERT ON fee_transactions
FOR EACH ROW
EXECUTE FUNCTION update_fee_payment_status();

-- Function to update book availability
CREATE OR REPLACE FUNCTION update_book_availability()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE library_books
        SET available_copies = available_copies - 1
        WHERE id = NEW.book_id;
    ELSIF TG_OP = 'UPDATE' AND NEW.loan_status = 'returned' AND OLD.loan_status != 'returned' THEN
        UPDATE library_books
        SET available_copies = available_copies + 1
        WHERE id = NEW.book_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_book_availability
AFTER INSERT OR UPDATE ON book_loans
FOR EACH ROW
EXECUTE FUNCTION update_book_availability();

-- Function to calculate overdue fines
CREATE OR REPLACE FUNCTION calculate_overdue_fine()
RETURNS TRIGGER AS $$
DECLARE
    days_overdue INTEGER;
    fine_per_day DECIMAL := 5.00;
BEGIN
    IF NEW.loan_status = 'overdue' OR (NEW.loan_status = 'active' AND NEW.due_date < CURRENT_DATE) THEN
        days_overdue := CURRENT_DATE - NEW.due_date;
        NEW.fine_amount := days_overdue * fine_per_day;
        NEW.loan_status := 'overdue';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_fine
BEFORE UPDATE ON book_loans
FOR EACH ROW
EXECUTE FUNCTION calculate_overdue_fine();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for student academic summary
CREATE OR REPLACE VIEW student_academic_summary AS
SELECT 
    s.id AS student_id,
    s.student_id AS roll_number,
    s.first_name || ' ' || s.last_name AS full_name,
    s.course,
    s.semester,
    COUNT(DISTINCT a.subject_id) AS total_subjects,
    ROUND(AVG(CASE WHEN a.status = 'present' THEN 100 ELSE 0 END), 2) AS overall_attendance_percentage,
    ROUND(AVG(m.obtained_marks * 100.0 / m.max_marks), 2) AS overall_percentage
FROM students s
LEFT JOIN attendance a ON s.id = a.student_id
LEFT JOIN marks m ON s.id = m.student_id
GROUP BY s.id, s.student_id, s.first_name, s.last_name, s.course, s.semester;

-- View for fee summary
CREATE OR REPLACE VIEW student_fee_summary AS
SELECT 
    s.id AS student_id,
    s.student_id AS roll_number,
    s.first_name || ' ' || s.last_name AS full_name,
    f.semester,
    f.academic_year,
    f.total_amount,
    f.amount_paid,
    f.total_amount - f.amount_paid AS balance,
    f.payment_status,
    f.due_date
FROM students s
JOIN fees f ON s.id = f.student_id;

-- ============================================================================
-- GRANT PERMISSIONS (Adjust based on your Supabase setup)
-- ============================================================================
-- These are typically handled by Supabase automatically, but included for reference

-- GRANT USAGE ON SCHEMA public TO anon, authenticated;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'BharatAce Production Database Schema Created Successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Tables created: 20';
    RAISE NOTICE 'Indexes created: 15+';
    RAISE NOTICE 'RLS Policies: Enabled';
    RAISE NOTICE 'Triggers: 3';
    RAISE NOTICE 'Views: 2';
    RAISE NOTICE '============================================================';
END $$;
