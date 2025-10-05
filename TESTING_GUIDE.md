# Quick Testing Guide

## 1. Start Backend (Terminal 1)

```bash
cd "d:\React Projects\Bharatace_mvd\backend"
uvicorn main:app --reload
```

**Expected Output:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
✅ AI AGENT SYSTEM INITIALIZATION COMPLETE!
```

**Verify Routes:**
Open http://127.0.0.1:8000/docs and check for `/student` endpoints:
- GET /student/attendance/summary
- GET /student/fees/status
- GET /student/timetable/today
- GET /student/library/loans
- GET /student/events/upcoming
- GET /student/marks/summary
- GET /student/profile

---

## 2. Start Frontend (Terminal 2)

```bash
cd "d:\React Projects\Bharatace_mvd\frontend"
npm run dev
```

**Expected Output:**
```
▲ Next.js 15.1.4
- Local: http://localhost:3000
✓ Starting...
✓ Ready in 2.3s
```

---

## 3. Test the Application

### Step 1: Login
1. Open http://localhost:3000
2. Click "Login" button
3. Use credentials:
   - Email: `sneha.patel@bharatace.edu.in`
   - Password: `password123`
4. Should redirect to `/dashboard`

### Step 2: Verify Dashboard Components

**Open Browser DevTools (F12) → Network Tab**

Expected API Calls (all should return 200 OK):
```
✓ GET /student/attendance/summary → 200 OK
✓ GET /student/fees/status → 200 OK
✓ GET /student/timetable/today → 200 OK
✓ GET /student/library/loans → 200 OK
✓ GET /student/events/upcoming → 200 OK
```

**Visual Checks:**

1. **Attendance Card**
   - Should show real attendance percentage (not 0%)
   - Should show total classes, present, absent counts
   - Status badge (Good/Warning/Critical)

2. **Fee Status Card**
   - Should show total amount, paid amount, pending
   - Should show payment status (Paid/Pending/Overdue)
   - Due date should be visible

3. **Today's Schedule Card**
   - Should show today's classes (or "No classes scheduled")
   - Each class should have time, subject, room

4. **Library Card**
   - Should show active book loans (or "No books issued")
   - Due dates should be visible
   - Overdue books highlighted in red

5. **Upcoming Events Card**
   - Should show next 3 events (or "No upcoming events")
   - Event types with colored badges

---

## 4. Test API Endpoints Directly

### Using Thunder Client / Postman

**Step 1: Get JWT Token**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "sneha.patel@bharatace.edu.in",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Step 2: Test Student Endpoints**

Copy the `access_token` and add to headers:
```
Authorization: Bearer eyJhbGc...
```

Then test each endpoint:

```bash
# Attendance Summary
GET http://localhost:8000/student/attendance/summary

# Fee Status
GET http://localhost:8000/student/fees/status

# Today's Timetable
GET http://localhost:8000/student/timetable/today

# Library Loans
GET http://localhost:8000/student/library/loans

# Upcoming Events (Public - No auth needed)
GET http://localhost:8000/student/events/upcoming

# Marks Summary
GET http://localhost:8000/student/marks/summary

# Student Profile
GET http://localhost:8000/student/profile
```

---

## 5. Expected Response Examples

### Attendance Summary
```json
{
  "total_classes": 120,
  "classes_attended": 95,
  "attendance_percentage": 79.17,
  "present_count": 95,
  "absent_count": 20,
  "late_count": 5
}
```

### Fee Status
```json
{
  "total_amount": 50000,
  "paid_amount": 48000,
  "pending_amount": 2000,
  "status": "pending",
  "late_fee": 0,
  "due_date": "2024-02-15"
}
```

### Today's Timetable
```json
[
  {
    "id": "...",
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "room_number": "A-101",
    "faculty_name": "Dr. Kumar"
  }
]
```

### Library Loans
```json
[
  {
    "id": "...",
    "book_title": "Introduction to Algorithms",
    "author": "Cormen",
    "isbn": "978-0262033848",
    "issue_date": "2024-01-15",
    "due_date": "2024-02-15",
    "return_date": null,
    "fine_amount": 0
  }
]
```

### Upcoming Events
```json
[
  {
    "id": "...",
    "title": "Tech Workshop",
    "description": "Learn React Advanced Patterns",
    "event_type": "workshop",
    "start_date": "2024-02-20",
    "location": "Auditorium"
  }
]
```

---

## 6. Troubleshooting

### Problem: All endpoints return 404

**Cause:** Student router not registered

**Fix:**
1. Check `backend/main.py` has:
   ```python
   from api.student_routes import router as student_router
   app.include_router(student_router)
   ```
2. Restart backend server

---

### Problem: Endpoints return 401 Unauthorized

**Cause:** Invalid or missing JWT token

**Fix:**
1. Login again to get fresh token
2. Check token is in localStorage: `localStorage.getItem('token')`
3. Verify token in request headers (DevTools → Network → Request Headers)

---

### Problem: Empty data returned (200 OK but empty arrays)

**Cause:** Database has no records for this student

**Fix:**
1. Check database has seed data for student
2. Verify student_id in JWT matches database records
3. Run seed script to populate test data

---

### Problem: Frontend shows "Loading..." forever

**Cause:** CORS issue or backend not running

**Fix:**
1. Verify backend is running on port 8000
2. Check browser console for CORS errors
3. Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in frontend/.env.local

---

### Problem: Components show hardcoded 0 values

**Cause:** API call failed, fallback to defaults

**Fix:**
1. Check browser DevTools → Network tab for failed requests
2. Check backend logs for errors
3. Verify endpoint returns correct data structure

---

## 7. Performance Verification

Open DevTools → Network tab and check response times:

**Expected:**
- Attendance: < 100ms
- Fees: < 100ms
- Timetable: < 150ms
- Library: < 150ms
- Events: < 100ms

**If slow (> 500ms):**
- Check database indexes
- Verify Supabase connection
- Check network latency

---

## 8. Success Criteria

✅ **All checks must pass:**

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Login works successfully
- [ ] Dashboard loads without infinite loading
- [ ] All 5 API calls return 200 OK (check Network tab)
- [ ] Attendance Card shows real data (not 0%)
- [ ] Fee Status Card shows real amounts
- [ ] Today's Schedule shows classes or "No classes"
- [ ] Library Card shows loans or "No books"
- [ ] Events Card shows events or "No events"
- [ ] All responses < 200ms (check Network tab)
- [ ] No AI agent calls in Network tab for dashboard data
- [ ] Chat interface still works (uses /ask endpoint)

---

## 9. Final Verification

Run this command in browser console (F12):

```javascript
// Check all API calls succeeded
const calls = performance.getEntriesByType('resource')
  .filter(r => r.name.includes('/student/'))
  .map(r => ({ 
    url: r.name, 
    time: r.duration.toFixed(0) + 'ms',
    status: 'Check Network tab'
  }));

console.table(calls);
```

**Expected Output:**
```
┌───┬─────────────────────────────────────┬────────┐
│ # │ url                                 │ time   │
├───┼─────────────────────────────────────┼────────┤
│ 0 │ /student/attendance/summary         │ 45ms   │
│ 1 │ /student/fees/status                │ 32ms   │
│ 2 │ /student/timetable/today            │ 58ms   │
│ 3 │ /student/library/loans              │ 67ms   │
│ 4 │ /student/events/upcoming            │ 41ms   │
└───┴─────────────────────────────────────┴────────┘
```

---

**Status:** ✅ Ready for Testing
**Estimated Time:** 15-20 minutes
