# Phase 6 - Quick Testing Guide

## ✅ What's Ready to Test Now

### 🖥️ Servers Running

1. **Student Portal**: http://localhost:3000 ✅ Working
2. **CMS Frontend**: http://localhost:3001 ✅ NEW - Just launched
3. **Backend API**: http://localhost:8000 ✅ Working with new admin routes

---

## 🧪 CMS Testing Steps

### Step 1: Access CMS
1. Open browser
2. Go to: http://localhost:3001
3. You should see the login modal

### Step 2: Login to CMS
**Test Credentials** (use existing admin credentials or create new):
- Email: `admin@bharatace.com` (if you've created this)
- Password: Your admin password

**If no admin exists**, you can:
- Create one in Supabase dashboard
- Or modify `LoginModal.tsx` to use hardcoded test credentials temporarily

### Step 3: Dashboard Tour
After login, you'll land on the dashboard which shows:

**Stats Cards** (Top row - 4 cards):
- Total Students: Should show 4 (Priya, Amit, Sneha, Rahul)
- Average CGPA: Should show ~8.36 (average of all 4 students)
- Attendance Rate: Calculated from attendance table
- Fee Collection: Percentage of fees collected vs total

**Charts** (4 visualizations):
1. **Branch-wise Performance** (Bar Chart)
   - CSE: Average CGPA of CSE students
   - ECE: Average CGPA of ECE students
   - ME: Average CGPA of ME students
   - Shows which branch performs best

2. **Student Distribution** (Pie Chart)
   - Shows how many students in each branch
   - Should see 4 students distributed across 3 branches

3. **Attendance Trends** (Line Chart)
   - Monthly attendance percentage
   - Will show data if attendance records exist

4. **Fee Collection by Semester** (Stacked Bar Chart)
   - Semester 1: Total fees, collected (green), pending (red)
   - Semester 2: Same breakdown
   - etc.

**Fee Summary** (Bottom section):
- Total Fees: Sum of all fee amounts
- Collected: Sum of all paid amounts
- Pending: Difference (Total - Collected)

**Quick Actions** (4 buttons):
- Manage Students → Takes you to `/students` (not built yet)
- Enter Marks → Takes you to `/marks` (not built yet)
- Mark Attendance → Takes you to `/attendance` (not built yet)
- Manage Fees → Takes you to `/fees` (not built yet)

### Step 4: Sidebar Navigation
Click on sidebar items to test routing:

**Working Pages**:
- ✅ Dashboard (current page)
- ✅ Knowledge Base (migrated from old CMS)

**Pending Pages** (will show 404 or empty):
- ⏳ Students
- ⏳ Marks
- ⏳ Attendance
- ⏳ Fees
- ⏳ Subjects
- ⏳ Events
- ⏳ Library
- ⏳ Settings

### Step 5: Knowledge Base Testing
1. Click "Knowledge Base" in sidebar
2. You should see:
   - **Add New Knowledge** form (same as old CMS)
   - **Existing Knowledge Base** list (all previous entries)
3. Test adding new knowledge entry
4. Verify it appears in the list
5. Test delete functionality

### Step 6: Logout
1. Click "Logout" button in sidebar (bottom)
2. Should redirect to login page
3. Session tokens should be cleared

---

## 🔧 Backend API Testing

### Test Admin Endpoints (Using Postman or curl)

**Get Admin Token First**:
```bash
POST http://localhost:8000/auth/login
Body: {
  "email": "admin@bharatace.com",
  "password": "your_password"
}
Response: {
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Test Analytics Endpoints**:

1. **Dashboard Stats**:
```bash
GET http://localhost:8000/admin/analytics/dashboard
Headers: Authorization: Bearer <token>

Expected Response:
{
  "total_students": 4,
  "average_cgpa": 8.36,
  "attendance_rate": 85.5,
  "fee_collection_rate": 75.0,
  "total_fees": 200000,
  "collected_fees": 150000
}
```

2. **Student Performance**:
```bash
GET http://localhost:8000/admin/analytics/performance
Headers: Authorization: Bearer <token>

Expected Response:
{
  "performance": [
    {
      "branch": "CSE",
      "average_cgpa": 9.0,
      "student_count": 2
    },
    {
      "branch": "ECE",
      "average_cgpa": 8.0,
      "student_count": 1
    },
    {
      "branch": "ME",
      "average_cgpa": 7.43,
      "student_count": 1
    }
  ]
}
```

3. **Attendance Trends**:
```bash
GET http://localhost:8000/admin/analytics/attendance-trends
Headers: Authorization: Bearer <token>

Expected Response:
{
  "trends": [
    {
      "month": "2024-01",
      "attendance_percentage": 88.5,
      "total_records": 120
    },
    ...
  ]
}
```

4. **Fee Collection**:
```bash
GET http://localhost:8000/admin/analytics/fee-collection
Headers: Authorization: Bearer <token>

Expected Response:
{
  "collection": [
    {
      "semester": 1,
      "total_fees": 100000,
      "collected": 75000,
      "pending": 25000,
      "collection_rate": 75.0
    },
    ...
  ]
}
```

**Test Student Endpoints**:

```bash
# Get all students
GET http://localhost:8000/admin/students
Headers: Authorization: Bearer <token>

# Get specific student with full profile
GET http://localhost:8000/admin/students/<student_id>
Headers: Authorization: Bearer <token>

# Search students
GET http://localhost:8000/admin/students?search=Sneha
Headers: Authorization: Bearer <token>

# Filter by branch
GET http://localhost:8000/admin/students?branch=CSE
Headers: Authorization: Bearer <token>
```

**Test Marks Endpoints**:

```bash
# Get all marks
GET http://localhost:8000/admin/marks
Headers: Authorization: Bearer <token>

# Get marks for specific student
GET http://localhost:8000/admin/marks?student_id=<id>
Headers: Authorization: Bearer <token>

# Create new mark (auto CGPA calculation)
POST http://localhost:8000/admin/marks
Headers: Authorization: Bearer <token>
Body: {
  "student_id": "7e749a03-042b-48f3-a768-412e66a0e7f0",
  "subject_id": "<subject_id>",
  "exam_type": "Mid Term",
  "obtained_marks": 85,
  "max_marks": 100,
  "exam_date": "2024-12-01"
}
```

---

## 🐛 Known Issues & Limitations

### Current Limitations
1. **No Student/Marks/Attendance/Fees UI**: Backend ready, frontend pending
2. **Settings Page Not Built**: Only navigation link exists
3. **No User Management**: Single admin login only
4. **No Export Functionality**: Charts visible only, no download
5. **No Bulk Import**: CSV import not implemented

### Expected Behaviors
1. **Dashboard May Show 0s**: If no data in attendance/fees tables
2. **Empty Charts**: If no records for performance/trends
3. **404 Errors**: When clicking unbuilt module links
4. **Slow Initial Load**: Charts calculate on first render

### Not Bugs (By Design)
1. **No Dark Mode Toggle**: Auto-detects system preference
2. **No Search in Dashboard**: Search is in individual modules
3. **No Notifications**: Toast system not yet implemented
4. **Logout Requires Refresh**: Session cleared, manual navigation to login

---

## ✅ Success Indicators

### Dashboard Loaded Successfully
- ✅ 4 stat cards display numbers
- ✅ At least 1 chart shows data (performance bar chart should work)
- ✅ No console errors
- ✅ Quick action buttons are clickable

### Backend API Working
- ✅ `/admin/analytics/dashboard` returns JSON with stats
- ✅ `/admin/analytics/performance` returns branch data
- ✅ `/admin/students` returns all 4 demo students
- ✅ No 500 errors, only 200/404

### Navigation Working
- ✅ Sidebar opens on mobile (hamburger menu)
- ✅ Clicking links changes URL
- ✅ Active link highlights in indigo
- ✅ Logout redirects to home page

### Authentication Working
- ✅ Login sets tokens in sessionStorage
- ✅ Protected routes redirect to login if no token
- ✅ API calls include Bearer token automatically
- ✅ 401 errors trigger logout

---

## 🔍 Debugging Tips

### If Dashboard Shows 0s
1. Check backend terminal for errors
2. Open browser DevTools → Network tab
3. Look for failed API calls (red)
4. Check response JSON for error messages

### If Charts Don't Render
1. Open browser console (F12)
2. Look for Recharts errors
3. Verify data format matches expected shape
4. Check if data arrays are empty

### If Login Fails
1. Verify admin user exists in Supabase
2. Check email/password are correct
3. Look at Network tab for /auth/login call
4. Check if token is saved in sessionStorage

### If Navigation Broken
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check if Next.js compiled successfully
4. Restart CMS frontend server

---

## 📊 Expected Data (Current Database)

### Students (4 total)
1. **Sneha Patel** (CSE, Semester 5, CGPA: 9.21)
2. **Priya Sharma** (CSE, Semester 3, CGPA: 9.0)
3. **Amit Kumar** (ECE, Semester 3, CGPA: 8.0)
4. **Rahul Singh** (ME, Semester 3, CGPA: 7.43)

### Marks (192 records)
- 48 marks per student (4 students × 48)
- Subjects: 6 subjects per student
- Exam types: Mid Term, End Term, Quiz, Assignment

### Attendance (Variable)
- Check if attendance table has records
- If empty, attendance chart will be flat/empty

### Fees (Variable)
- Check if fees table has records
- If empty, fee collection will show 0%

---

## 🚀 Next Steps After Testing

If everything works:
1. ✅ Mark Phase 6 Session 1 as successful
2. ✅ Proceed to Student Management Module (next priority)
3. ✅ Continue building remaining CRUD modules

If issues found:
1. Document errors with screenshots
2. Check backend logs for stack traces
3. Verify database has expected data
4. Report to developer for fixes

---

## 💬 Support

**Check Logs**:
- Backend: Terminal running `python -m uvicorn...`
- CMS Frontend: Terminal running `npm run dev`
- Browser: DevTools Console (F12)

**Common Commands**:
```bash
# Restart CMS frontend
cd "d:\React Projects\Bharatace_mvd\cms-frontend"
npm run dev

# Restart backend
cd "d:\React Projects\Bharatace_mvd\backend"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Check database
# Go to Supabase dashboard → Table Editor
```

---

**HAPPY TESTING! 🎉**

*If dashboard loads with charts and stats, Phase 6 foundation is successful!*
