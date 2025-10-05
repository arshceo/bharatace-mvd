# 🧪 ADMIN CMS TESTING GUIDE
## How to Test the New Admin Portal

---

## ⚡ QUICK START (5 Minutes)

### Step 1: Create Admin Tables in Supabase

1. **Open Supabase**:
   - Go to https://supabase.com/dashboard
   - Select your project
   - Click "SQL Editor" in left sidebar

2. **Run Migration**:
   - Open file: `backend/migrations/create_admin_tables.sql`
   - Copy **all content** (70 lines)
   - Paste in Supabase SQL Editor
   - Click "Run" (or press F5)

3. **Verify Success**:
   You should see:
   ```
   ✓ Success. No rows returned
   ```

4. **Check Tables Created**:
   - Go to "Table Editor"
   - You should see 3 new tables:
     * `admin_users` (with 1 row - the demo admin)
     * `faculty` (empty)
     * `faculty_subject_assignments` (empty)

---

### Step 2: Restart Backend Server

**Option A: If server is running in terminal**
```powershell
# Press Ctrl+C to stop
# Then restart:
cd "d:\React Projects\Bharatace_mvd\backend"
python -m uvicorn main:app --reload
```

**Option B: If not running**
```powershell
cd "d:\React Projects\Bharatace_mvd\backend"
python -m uvicorn main:app --reload
```

**Expected Output**:
```
✅ STEP 1/7: Environment loaded
✅ STEP 2/7: Gemini API initialized
✅ STEP 3/7: Knowledge base loaded (11 documents)
✅ STEP 4/7: Vector index created
✅ STEP 5/7: Tools initialized (16 tools)
✅ STEP 6/7: SmartAgent created
✅ STEP 7/7: Agent validated

✅ AI AGENT SYSTEM INITIALIZATION COMPLETE!
📊 Total Documents Indexed: 11
🛠️ Total Tools Available: 16

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### Step 3: Test Admin Login in Browser

1. **Open Browser**:
   - Go to: http://localhost:3000/admin/login

2. **You Should See**:
   - Blue gradient login page
   - Lock icon at top
   - "Admin Portal" heading
   - Email and password fields
   - Demo credentials box

3. **Enter Credentials**:
   - Email: `admin@bharatace.com`
   - Password: `admin123`
   - Click "Sign In"

4. **Expected Result**:
   - ✅ Should redirect to: http://localhost:3000/admin/dashboard
   - ✅ Should see sidebar on left
   - ✅ Should see dashboard with charts

---

### Step 4: Verify Dashboard

**Check Stat Cards** (Top row):
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 👥 Total    │ 👨‍🏫 Total   │ 📈 Avg      │ 📅 Avg      │
│ Students: 4 │ Faculty: 0  │ CGPA: 8.4   │ Attend: 89% │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Check Charts**:
1. **Department Distribution** (Pie Chart)
   - Should show CSE, ECE, ME, Civil
   - Each with 1 student (25%)

2. **CGPA Distribution** (Bar Chart)
   - Should show distribution across ranges
   - Most students in 8.0-8.9 and 9.0-10.0

3. **Enrollment Trend** (Line Chart)
   - Should show monthly enrollment

4. **AI Usage Stats** (Purple gradient box)
   - Total Queries: 1250
   - Queries Today: 47
   - Most Asked: Attendance

---

## 🔬 DETAILED API TESTING

### Test 1: Admin Login

**Request**:
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@bharatace.com",
    "password": "admin123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin": {
    "id": "some-uuid",
    "email": "admin@bharatace.com",
    "full_name": "Super Admin",
    "role": "super_admin",
    "institution_id": null,
    "permissions": {
      "can_manage_institutions": true,
      "can_manage_students": true,
      ...
    },
    "is_active": true,
    "created_at": "2024-..."
  }
}
```

**Copy the `access_token` for next tests!**

---

### Test 2: Get Admin Info

**Request**:
```bash
curl http://localhost:8000/admin/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
{
  "id": "some-uuid",
  "email": "admin@bharatace.com",
  "full_name": "Super Admin",
  "role": "super_admin",
  ...
}
```

---

### Test 3: Get Dashboard Data

**Request**:
```bash
curl http://localhost:8000/admin/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
{
  "stats": {
    "total_students": 4,
    "total_faculty": 0,
    "total_departments": 4,
    "total_subjects": 4,
    "average_cgpa": 8.38,
    "average_attendance": 89.06,
    "fee_collection_rate": 62.5,
    "active_events": 0,
    "pending_fee_amount": 150000.0,
    "students_with_shortage": 0
  },
  "enrollment_trend": [...],
  "department_distribution": [...],
  "cgpa_distribution": [...],
  "ai_usage": {...}
}
```

---

### Test 4: Invalid Login

**Request**:
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@email.com",
    "password": "wrongpassword"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid credentials"
}
```

---

### Test 5: Unauthenticated Dashboard Access

**Request**:
```bash
curl http://localhost:8000/admin/dashboard
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

---

## 🎯 FRONTEND TESTING CHECKLIST

### Login Page Tests:
- [ ] Page loads at http://localhost:3000/admin/login
- [ ] Form has email and password fields
- [ ] Demo credentials visible in blue box
- [ ] Empty form shows browser validation
- [ ] Wrong credentials show error message
- [ ] Correct credentials redirect to dashboard
- [ ] Token stored in localStorage after login

### Dashboard Tests:
- [ ] Dashboard loads at http://localhost:3000/admin/dashboard
- [ ] 8 stat cards display correct data
- [ ] Department pie chart renders
- [ ] CGPA bar chart renders
- [ ] Enrollment line chart renders
- [ ] AI usage stats show in purple box
- [ ] Sidebar has 12 menu items
- [ ] Clicking sidebar items attempts navigation
- [ ] Admin name shows in sidebar footer
- [ ] Logout button present

### Sidebar Tests:
- [ ] Sidebar starts open (wide)
- [ ] Menu button (X icon) collapses sidebar
- [ ] Collapsed sidebar shows only icons
- [ ] Menu items have hover effect
- [ ] Admin avatar shows first letter of name
- [ ] Role displayed under name

### Logout Tests:
- [ ] Click logout button
- [ ] Redirects to /admin/login
- [ ] Token removed from localStorage
- [ ] Cannot access /admin/dashboard without login
- [ ] Auto-redirects to login if token missing

---

## 🐛 TROUBLESHOOTING

### Issue: Tables don't exist

**Error in browser console**:
```
Failed to fetch dashboard data
```

**Solution**:
1. Check Supabase Table Editor
2. Verify `admin_users`, `faculty`, `faculty_subject_assignments` exist
3. Re-run SQL migration if missing

---

### Issue: Backend not loading admin routes

**Error in browser console**:
```
POST http://localhost:8000/admin/login 404 (Not Found)
```

**Solution**:
1. Restart backend server
2. Check terminal for errors
3. Verify `backend/main.py` has these lines:
   ```python
   from api.admin_auth import router as admin_auth_router
   from api.admin_dashboard import router as admin_dashboard_router
   app.include_router(admin_auth_router)
   app.include_router(admin_dashboard_router)
   ```

---

### Issue: Import errors in VSCode

**Red squiggles on imports**:
```python
from models.admin import AdminCreate  # Red squiggle
```

**Solution**:
- This is just IDE path resolution
- Code will run fine
- Restart VSCode or reload window if bothering you

---

### Issue: Frontend won't start

**Error**:
```
Module 'lucide-react' not found
```

**Solution**:
```powershell
cd "d:\React Projects\Bharatace_mvd\frontend"
npm install
```

---

### Issue: Login succeeds but dashboard shows errors

**Check**:
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests

**Common causes**:
- Missing authorization header
- Token expired
- Database connection issue

**Solution**:
1. Logout and login again
2. Check backend terminal for errors
3. Verify token in localStorage

---

## 📊 EXPECTED DATA

Based on your current database (4 students, 192 marks):

### Stats Should Show:
- **Total Students**: 4
- **Total Faculty**: 0 (we haven't added any yet)
- **Total Departments**: 4 (CSE, ECE, ME, Civil)
- **Total Subjects**: 4
- **Avg CGPA**: ~8.38 (Priya: 9.0, Amit: 8.0, Sneha: 9.21, Rahul: 7.43)
- **Avg Attendance**: ~89.06%
- **Fee Collection**: ~62.5%
- **Pending Fees**: ₹150,000

### Department Distribution:
- CSE: 1 student (25%)
- ECE: 1 student (25%)
- ME: 1 student (25%)
- Civil: 1 student (25%)

### CGPA Distribution:
- 9.0-10.0: 2 students (Priya, Sneha)
- 8.0-8.9: 1 student (Amit)
- 7.0-7.9: 1 student (Rahul)

---

## ✅ SUCCESS CRITERIA

Your admin portal is working correctly if:

1. ✅ Login page loads without errors
2. ✅ Can login with admin@bharatace.com / admin123
3. ✅ Dashboard shows 4 total students
4. ✅ All 4 charts render without errors
5. ✅ Sidebar shows 12 menu items
6. ✅ Admin name "Super Admin" appears in sidebar
7. ✅ Logout button works and redirects to login
8. ✅ Cannot access dashboard without valid token
9. ✅ No console errors in browser DevTools
10. ✅ Backend terminal shows no errors

---

## 🎉 WHAT'S WORKING

After successful testing, you'll have:

✅ **Admin Authentication System**
- Secure login with JWT tokens
- Role-based permissions
- 24-hour token expiry

✅ **Analytics Dashboard**
- Real-time statistics from your database
- 4 interactive charts
- AI usage tracking

✅ **Professional UI**
- Responsive sidebar navigation
- Beautiful gradient design
- Loading states
- Error handling

✅ **Foundation for CMS**
- Ready to add Student Management (Sprint 2)
- Ready to add Faculty Management (Sprint 2)
- Ready to add Marks Entry (Sprint 3)

---

## 🚀 NEXT STEPS

Once testing is complete:

1. **Document any issues found**
2. **Fix critical bugs**
3. **Polish UI/UX**
4. **Move to Sprint 2: Student Management**

Sprint 2 will add:
- Student list with search/filter/sort
- Add/Edit student forms
- Bulk CSV import
- Faculty management
- Department & subject CRUD

---

*Last Updated: Today*  
*Expected Testing Time: 15-20 minutes*  
*Status: Ready for Testing*
