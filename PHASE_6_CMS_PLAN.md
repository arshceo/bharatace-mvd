# PHASE 6: PRODUCTION-LEVEL CMS

## 🎯 Objective
Build a comprehensive **Admin Dashboard & CMS** to manage:
- Multiple institutions (multi-tenancy)
- Students, faculty, courses
- Marks, attendance, fees
- Events, library, timetable
- AI agent knowledge base

---

## 🏗️ ARCHITECTURE OVERVIEW

### Admin Portal Structure
```
BharatAce Admin CMS
├── Institution Management
│   ├── Create/Edit institutions
│   ├── Configure settings
│   └── Manage branding
├── User Management
│   ├── Students (bulk import/export)
│   ├── Faculty
│   ├── Admins
│   └── Role-based access control
├── Academic Management
│   ├── Departments
│   ├── Courses/Subjects
│   ├── Semesters
│   └── Academic calendar
├── Data Management
│   ├── Marks entry & import
│   ├── Attendance tracking
│   ├── Fee management
│   └── Bulk operations
├── Content Management
│   ├── Knowledge base editor
│   ├── Event creation
│   ├── Announcements
│   └── Library catalog
└── Analytics & Reports
    ├── Student performance
    ├── Attendance reports
    ├── Financial reports
    └── AI usage statistics
```

---

## 📋 FEATURE BREAKDOWN

### 1. Multi-Tenant Institution Management

#### Features:
- ✅ **Institution CRUD**
  - Create new colleges/universities
  - Edit institution details
  - Configure logos, colors, branding
  - Set academic year settings

- ✅ **Subdomain/URL Management**
  - Each institution gets unique URL
  - Example: bharatace.mvd.app, mitcollege.mvd.app
  - Custom domain support (future)

- ✅ **Settings & Configuration**
  - Academic calendar
  - Grading system (10-point, percentage, letter grades)
  - Fee structure templates
  - Attendance requirements (75% minimum, etc.)

#### Database Schema Updates:
```sql
-- Add to institutions table
ALTER TABLE institutions ADD COLUMN subdomain VARCHAR(50) UNIQUE;
ALTER TABLE institutions ADD COLUMN primary_color VARCHAR(7);
ALTER TABLE institutions ADD COLUMN logo_url TEXT;
ALTER TABLE institutions ADD COLUMN academic_year VARCHAR(20);
ALTER TABLE institutions ADD COLUMN grading_system VARCHAR(20);
ALTER TABLE institutions ADD COLUMN min_attendance_percentage DECIMAL(5,2);
```

---

### 2. User Management System

#### A. Student Management

**Features:**
- ✅ **Bulk Import** (CSV/Excel)
  - Upload student list
  - Auto-generate roll numbers
  - Auto-create credentials
  - Send welcome emails

- ✅ **Individual Add/Edit**
  - Form-based entry
  - Photo upload
  - Guardian information
  - Document uploads

- ✅ **Student Profile**
  - Personal details
  - Academic history
  - Contact information
  - Emergency contacts

**CSV Import Format:**
```csv
full_name,email,roll_number,department,semester,date_of_birth,phone,guardian_name,guardian_phone
Priya Sharma,priya@college.edu,CS2021001,Computer Science,5,2003-05-15,9876543210,Mr. Sharma,9876543211
```

#### B. Faculty Management

**Features:**
- ✅ **Faculty Profiles**
  - Personal & professional details
  - Qualifications
  - Subjects taught
  - Class assignments

- ✅ **Faculty Permissions**
  - Can enter marks for assigned subjects
  - Can mark attendance for assigned classes
  - View student performance

**New Table:**
```sql
CREATE TABLE faculty (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id),
    employee_id VARCHAR(50) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    designation VARCHAR(100),
    phone VARCHAR(20),
    join_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE faculty_subject_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    faculty_id UUID REFERENCES faculty(id),
    subject_id UUID REFERENCES subjects(id),
    semester INT,
    academic_year VARCHAR(20)
);
```

#### C. Admin Management

**Features:**
- ✅ **Role-Based Access Control (RBAC)**
  - Super Admin (platform level)
  - Institution Admin (per college)
  - Department Admin (per department)
  - Faculty (limited access)

**New Table:**
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL, -- 'super_admin', 'institution_admin', 'department_admin'
    permissions JSONB, -- {'can_edit_marks': true, 'can_delete_students': false}
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3. Academic Management

#### A. Department Management
- ✅ Create/Edit departments
- ✅ Assign HOD (Head of Department)
- ✅ Department-wise student/faculty count

#### B. Subject/Course Management
- ✅ **Bulk Subject Creation**
  - Import from CSV
  - Template-based (CS, ECE, IT standard subjects)

- ✅ **Subject Details**
  - Subject code, name
  - Credits
  - Theory/Practical/Lab
  - Prerequisites
  - Syllabus upload

#### C. Semester Management
- ✅ Create semester structure
- ✅ Assign subjects to semesters
- ✅ Set exam schedules

---

### 4. Data Management

#### A. Marks Entry System

**Features:**
- ✅ **Bulk Import** (Excel/CSV)
  ```csv
  roll_number,subject_code,exam_type,obtained_marks,max_marks,exam_date
  CS2021001,CS301,midterm,85,100,2025-08-20
  ```

- ✅ **Manual Entry Form**
  - Select subject, exam type
  - Enter marks for all students
  - Validate (0-max_marks)

- ✅ **Edit/Delete** existing marks

- ✅ **Auto CGPA Calculation**
  - Trigger on marks insert/update
  - Update students.cgpa automatically

**New Function:**
```sql
CREATE OR REPLACE FUNCTION update_student_cgpa()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate CGPA from marks and update students table
    UPDATE students 
    SET cgpa = (calculated_cgpa)
    WHERE id = NEW.student_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER marks_update_trigger
AFTER INSERT OR UPDATE ON marks
FOR EACH ROW EXECUTE FUNCTION update_student_cgpa();
```

#### B. Attendance Management

**Features:**
- ✅ **Daily Attendance Entry**
  - Date picker
  - Subject selection
  - Mark all present/absent
  - Individual toggles

- ✅ **Bulk Import** (CSV)
  ```csv
  date,subject_code,roll_number,status
  2025-10-01,CS301,CS2021001,present
  ```

- ✅ **Attendance Reports**
  - Student-wise
  - Subject-wise
  - Date-range filters

- ✅ **Shortage Alerts**
  - Auto-flag students <75%
  - Send email notifications

#### C. Fee Management

**Features:**
- ✅ **Fee Structure Templates**
  - Per semester/year
  - Category-wise (tuition, lab, library)
  - Hostel fees

- ✅ **Fee Assignment**
  - Bulk assign to students
  - Override for specific students

- ✅ **Payment Recording**
  - Manual entry
  - Payment gateway integration (future)
  - Receipt generation

- ✅ **Defaulter Reports**
  - Overdue fees list
  - Send reminders

---

### 5. Content Management

#### A. Knowledge Base Editor

**Features:**
- ✅ **Rich Text Editor**
  - Markdown support
  - Upload images
  - Embed videos/links

- ✅ **Categories & Tags**
  - Organize by topic
  - Search & filter

- ✅ **Version Control**
  - Track changes
  - Rollback to previous versions

- ✅ **AI Training**
  - Mark as "AI-visible"
  - Update vector embeddings
  - Test responses

**Enhanced Table:**
```sql
ALTER TABLE knowledge_base ADD COLUMN category VARCHAR(100);
ALTER TABLE knowledge_base ADD COLUMN tags TEXT[];
ALTER TABLE knowledge_base ADD COLUMN version INT DEFAULT 1;
ALTER TABLE knowledge_base ADD COLUMN is_ai_visible BOOLEAN DEFAULT true;
ALTER TABLE knowledge_base ADD COLUMN author_id UUID REFERENCES admin_users(id);
ALTER TABLE knowledge_base ADD COLUMN last_updated_by UUID REFERENCES admin_users(id);
```

#### B. Event Management

**Features:**
- ✅ **Event Creation**
  - Title, description, date/time
  - Location (physical/virtual)
  - Capacity limits
  - Registration deadlines

- ✅ **Event Categories**
  - Technical, Cultural, Sports
  - Workshops, Seminars

- ✅ **Registration Management**
  - View registrations
  - Export attendee list
  - Send confirmations

- ✅ **Event Calendar View**
  - Monthly calendar
  - Filter by category

#### C. Announcement System

**New Feature:**
- ✅ **Create Announcements**
  - Important notices
  - Holiday notifications
  - Exam schedules

- ✅ **Target Audience**
  - All students
  - Specific department/semester
  - Individual students

- ✅ **Notification Channels**
  - Email
  - In-app notifications
  - SMS (future)

**New Table:**
```sql
CREATE TABLE announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID REFERENCES institutions(id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    target_audience VARCHAR(50), -- 'all', 'department', 'semester', 'individual'
    target_filter JSONB, -- {'department': 'CS', 'semester': 5}
    priority VARCHAR(20), -- 'high', 'medium', 'low'
    created_by UUID REFERENCES admin_users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### D. Library Management

**Features:**
- ✅ **Book Catalog Management**
  - Add/Edit/Delete books
  - ISBN, author, publisher
  - Categories & tags
  - Quantity tracking

- ✅ **Book Reservations**
  - View pending reservations
  - Approve/Reject
  - Set due dates

- ✅ **Overdue Management**
  - Auto-calculate fines
  - Send reminders
  - Block if overdue

---

### 6. Analytics & Reports

#### A. Dashboard Analytics

**Features:**
- ✅ **Key Metrics Cards**
  - Total students, faculty
  - Average CGPA
  - Attendance percentage
  - Fee collection rate

- ✅ **Charts & Graphs**
  - Student enrollment trends
  - Department-wise distribution
  - CGPA distribution histogram
  - Attendance over time

- ✅ **AI Usage Stats**
  - Total queries handled
  - Most asked questions
  - Response accuracy (user feedback)
  - Tool usage breakdown

#### B. Student Reports

**Reports:**
- ✅ **Performance Report**
  - CGPA trend over semesters
  - Subject-wise breakdown
  - Comparison with class average
  - Rank in class

- ✅ **Attendance Report**
  - Subject-wise attendance
  - Monthly trends
  - Shortage alerts

- ✅ **Fee Statement**
  - Total fees, paid, pending
  - Payment history
  - Due dates

**Export Options:**
- PDF, Excel, CSV

#### C. Institutional Reports

**Reports:**
- ✅ **Academic Performance**
  - Department-wise CGPA
  - Subject pass percentages
  - Topper lists

- ✅ **Attendance Analytics**
  - Overall attendance percentage
  - Subject-wise trends
  - Student shortage list

- ✅ **Financial Reports**
  - Fee collection summary
  - Defaulter list
  - Revenue projections

- ✅ **AI Agent Reports**
  - Query volume by category
  - Most used tools
  - Student engagement metrics

---

## 🎨 ADMIN UI/UX DESIGN

### Technology Stack
```
Frontend (Admin Panel):
- Framework: Next.js 15 (App Router)
- UI Library: shadcn/ui (Radix UI + Tailwind)
- Charts: Recharts / Chart.js
- Tables: TanStack Table (React Table v8)
- Forms: React Hook Form + Zod validation
- Rich Editor: Tiptap / Lexical
- File Upload: UploadThing / Cloudinary
- Icons: Lucide React
```

### Page Structure
```
/admin
├── /login                    # Admin login
├── /dashboard                # Main dashboard (analytics)
├── /institutions             # Institution management
│   ├── /list
│   ├── /create
│   └── /[id]/edit
├── /students                 # Student management
│   ├── /list                 # Data table with search/filter
│   ├── /create               # Add single student
│   ├── /import               # Bulk import CSV
│   └── /[id]                 # Student profile
├── /faculty                  # Faculty management
│   ├── /list
│   ├── /create
│   └── /[id]
├── /departments              # Department management
├── /subjects                 # Subject management
│   ├── /list
│   └── /import
├── /marks                    # Marks entry
│   ├── /entry                # Manual entry form
│   ├── /import               # Bulk import
│   └── /reports
├── /attendance               # Attendance management
│   ├── /entry                # Daily entry
│   ├── /import
│   └── /reports
├── /fees                     # Fee management
│   ├── /structure            # Fee templates
│   ├── /assign               # Assign to students
│   ├── /payments             # Record payments
│   └── /defaulters
├── /library                  # Library management
│   ├── /books
│   ├── /loans
│   └── /reservations
├── /events                   # Event management
│   ├── /list
│   ├── /create
│   └── /registrations
├── /knowledge-base           # CMS for AI training
│   ├── /articles
│   ├── /create
│   └── /categories
├── /announcements            # Announcement system
├── /reports                  # Report generation
│   ├── /students
│   ├── /academic
│   ├── /financial
│   └── /ai-analytics
└── /settings                 # System settings
    ├── /institution
    ├── /users
    └── /integrations
```

---

## 🚀 IMPLEMENTATION PLAN

### Sprint 1: Core Admin Foundation (Week 1)
**Goal**: Basic admin portal with authentication

**Tasks**:
1. Create admin database schema
2. Build admin authentication system
3. Create admin layout (sidebar, navbar)
4. Dashboard with basic metrics
5. Admin user management

**Files to Create**:
- `backend/models/admin.py`
- `backend/api/admin_auth.py`
- `backend/api/admin_routes.py`
- `frontend/src/app/admin/layout.tsx`
- `frontend/src/app/admin/dashboard/page.tsx`
- `frontend/src/components/admin/Sidebar.tsx`

**Estimated Time**: 2-3 days

---

### Sprint 2: Student & Faculty Management (Week 1)
**Goal**: CRUD operations for users

**Tasks**:
1. Student list with data table (search, filter, pagination)
2. Add/Edit student forms
3. Bulk CSV import functionality
4. Faculty management (similar to students)
5. Department & subject management

**Files to Create**:
- `frontend/src/app/admin/students/page.tsx`
- `frontend/src/components/admin/StudentTable.tsx`
- `frontend/src/components/admin/ImportCSV.tsx`
- `backend/api/bulk_import.py`
- `backend/utils/csv_parser.py`

**Estimated Time**: 3-4 days

---

### Sprint 3: Data Entry Systems (Week 2)
**Goal**: Marks and attendance entry

**Tasks**:
1. Marks entry form (subject, exam type, marks)
2. Bulk marks import from CSV
3. Attendance entry interface (daily)
4. Attendance shortage alerts
5. Auto CGPA calculation trigger

**Files to Create**:
- `frontend/src/app/admin/marks/page.tsx`
- `frontend/src/app/admin/attendance/page.tsx`
- `backend/api/marks_admin.py`
- `backend/api/attendance_admin.py`
- `backend/database/triggers.sql`

**Estimated Time**: 3-4 days

---

### Sprint 4: Content & Analytics (Week 2)
**Goal**: CMS and reporting

**Tasks**:
1. Knowledge base editor (rich text)
2. Event management system
3. Analytics dashboard with charts
4. Report generation (PDF/Excel export)
5. AI usage statistics

**Files to Create**:
- `frontend/src/app/admin/knowledge-base/page.tsx`
- `frontend/src/components/admin/RichTextEditor.tsx`
- `frontend/src/app/admin/reports/page.tsx`
- `backend/api/reports.py`
- `backend/utils/pdf_generator.py`

**Estimated Time**: 4-5 days

---

### Sprint 5: Multi-Tenancy & Polish (Week 3)
**Goal**: Multi-institution support

**Tasks**:
1. Institution CRUD
2. Subdomain routing
3. Institution-specific branding
4. Role-based access control (RBAC)
5. UI/UX polish and testing

**Files to Create**:
- `frontend/src/app/admin/institutions/page.tsx`
- `backend/middleware/tenant_isolation.py`
- `backend/api/institution_routes.py`
- `frontend/src/components/admin/BrandingSettings.tsx`

**Estimated Time**: 5-6 days

---

## 📊 SUCCESS CRITERIA

### Functional Requirements
- [ ] Admin can login and access dashboard
- [ ] Admin can add/edit/delete students
- [ ] Admin can bulk import students from CSV
- [ ] Admin can enter marks manually or via CSV
- [ ] Admin can mark daily attendance
- [ ] CGPA auto-updates when marks are entered
- [ ] Admin can create events and view registrations
- [ ] Admin can edit knowledge base articles
- [ ] Admin can generate and export reports
- [ ] System supports multiple institutions

### Non-Functional Requirements
- [ ] Data table loads <500ms for 1000 students
- [ ] CSV import processes 100 students in <5s
- [ ] Forms have client-side validation
- [ ] UI is responsive (mobile, tablet, desktop)
- [ ] All admin actions are logged (audit trail)
- [ ] RLS ensures data isolation per institution

---

## 🎯 NEXT IMMEDIATE STEPS

Would you like me to:

1. **Start with Sprint 1** - Create admin authentication & dashboard?
2. **Focus on specific feature** - Which is highest priority?
   - Student bulk import?
   - Marks entry system?
   - Analytics dashboard?
3. **Show UI mockups** - Design the admin interface first?

Let me know which direction you'd like to take! 🚀
