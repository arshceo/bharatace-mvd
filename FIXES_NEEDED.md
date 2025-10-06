# Critical Fixes Required

## ✅ COMPLETED FIXES

### 1. Attendance Page - Student Name Field
**Problem**: Using `student.name` which doesn't exist in database
**Solution**: Updated to use `full_name` or fallback to `first_name + last_name`

**Files Fixed:**
- `cms-frontend/src/app/attendance/page.tsx`
  - Updated Student interface
  - Fixed all references to student.name
  - Added fallback for enrollment_number/roll_number
  - Fixed branch/department filtering

---

## ❌ REMAINING ISSUES

### 2. Events API - Column Name Mismatch ⚠️ HIGH PRIORITY

**Problem**: Backend code uses `event_date` column, but database schema has `start_date`

**Error**: Internal Server Error (500) when fetching events

**Location**: `backend/api/admin_routes.py` line 488

**Current Code** (WRONG):
```python
query = supabase.table('events').select('*').order('event_date', desc=True)
```

**Should Be**:
```python
query = supabase.table('events').select('*').order('start_date', desc=True)
```

**Database Schema** (from `database_schema.sql`):
```sql
CREATE TABLE events (
    ...
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    ...
);
```

### Fix Required:
Update `backend/api/admin_routes.py`:

```python
@router.get("/events")
async def get_all_events(event_type: Optional[str] = None):
    """Get all events"""
    supabase = get_supabase_admin()
    
    # CHANGE THIS LINE:
    query = supabase.table('events').select('*').order('start_date', desc=True)
    
    if event_type:
        query = query.eq('event_type', event_type)
    
    response = query.execute()
    return {"events": response.data}
```

Also check the EventCreate model and any other references to `event_date` in the events endpoints.

---

### 3. Fees Page - No Data Display UI ⚠️ MEDIUM PRIORITY

**Problem**: Fees page only shows count, doesn't display actual fee records

**Current State**:
- Shows: "Total Fee Records: 4"
- Missing: Table or cards to display individual fee records

**Location**: `cms-frontend/src/app/fees/page.tsx`

**What's Needed**:
Add a table to display fee records with columns:
- Student Name (from `students.full_name`)
- Semester
- Academic Year
- Total Amount
- Amount Paid
- Balance (total_amount - amount_paid)
- Payment Status (pending/partial/paid/overdue)
- Due Date
- Actions (View/Record Payment/Edit/Delete)

**Backend Data Structure** (from `admin_routes.py` line 356):
```python
query = supabase.table('fees').select('*, students(first_name, last_name, roll_number)')
```

So fees come with nested student data.

**Suggested UI Layout**:
```tsx
<table>
  <thead>
    <tr>
      <th>Student</th>
      <th>Roll Number</th>
      <th>Semester</th>
      <th>Total</th>
      <th>Paid</th>
      <th>Balance</th>
      <th>Status</th>
      <th>Due Date</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {feesData.map(fee => (
      <tr key={fee.id}>
        <td>{fee.students.full_name || `${fee.students.first_name} ${fee.students.last_name}`}</td>
        <td>{fee.students.roll_number}</td>
        <td>{fee.semester}</td>
        <td>₹{fee.total_amount}</td>
        <td>₹{fee.amount_paid}</td>
        <td>₹{fee.total_amount - fee.amount_paid}</td>
        <td>
          <span className={getStatusColor(fee.payment_status)}>
            {fee.payment_status}
          </span>
        </td>
        <td>{new Date(fee.due_date).toLocaleDateString()}</td>
        <td>
          {/* Action buttons */}
        </td>
      </tr>
    ))}
  </tbody>
</table>
```

---

## VERIFICATION CHECKLIST

After applying fixes:

### Events:
- [ ] Backend starts without errors
- [ ] GET /admin/events returns 200 OK
- [ ] Events page loads without Network Error
- [ ] Events page displays events (or empty state if none)
- [ ] Can create new events
- [ ] Can edit/delete events

### Fees:
- [ ] Fees page displays table with fee records
- [ ] Shows student names correctly (using full_name)
- [ ] Displays all fee fields properly
- [ ] Can record payments
- [ ] Can create/edit/delete fee records
- [ ] Status badges show correct colors

### Attendance:
- [ ] Student names display correctly
- [ ] No "undefined.charAt(0)" errors
- [ ] Attendance stats calculate properly
- [ ] Can mark attendance in bulk
- [ ] Filters work (branch/semester)

---

## QUICK FIX COMMANDS

### Fix Events API (Backend):
```bash
cd backend
# Edit api/admin_routes.py line 488
# Change: order('event_date', desc=True)
# To:     order('start_date', desc=True)
```

### Test Events API:
```powershell
# After fix, test with:
Invoke-WebRequest -Uri "http://localhost:8000/admin/events" -Headers @{"Authorization"="Bearer your_token"}
```

### Update Fees Page (Frontend):
The fees page needs a complete table component added. Reference the students page or marks page for table structure examples.

---

## PRIORITY ORDER

1. **HIGH**: Fix Events API backend (2 minutes)
2. **MEDIUM**: Add Fees page UI table (30 minutes)
3. **COMPLETE**: Attendance page (already done ✅)

