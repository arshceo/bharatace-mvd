# CMS Admin Login Credentials

## 🔐 Admin Access

**URL**: http://localhost:3001

**Credentials**:
```
Email:    admin@bharatace.com
Password: Admin@123456
```

**Role**: Super Admin (Full Access)

---

## ✅ What's Fixed

### Previous Issue
- CMS was using `/auth/login` (student login endpoint)
- Showing student credentials (Sneha, etc.)
- Wrong authentication system

### Current Solution
- ✅ CMS now uses `/admin/login` (admin endpoint)
- ✅ Requires admin account from `admin_users` table
- ✅ Super admin has all permissions
- ✅ Separate authentication from student portal

---

## 🎯 Admin vs Student Portal

| Feature | Student Portal | CMS Admin Panel |
|---------|---------------|-----------------|
| URL | http://localhost:3000 | http://localhost:3001 |
| Login Endpoint | `/auth/login` | `/admin/login` |
| Database Table | `students` | `admin_users` |
| Token Type | Student JWT | Admin JWT |
| Permissions | Own data only | Full CRUD access |
| Features | View grades, attendance | Manage all data |

---

## 🔑 Admin Roles & Permissions

### Super Admin (current account)
All permissions enabled:
- ✅ Manage Institutions
- ✅ Manage Students
- ✅ Manage Faculty
- ✅ Enter Marks
- ✅ Mark Attendance
- ✅ Manage Fees
- ✅ Manage Library
- ✅ Manage Events
- ✅ Manage Knowledge Base
- ✅ View Reports
- ✅ Export Data
- ✅ Delete Records

### Institution Admin
Limited to institution scope:
- ✅ Manage Students
- ✅ Manage Faculty
- ✅ Enter Marks
- ✅ Mark Attendance
- ✅ Manage Fees
- ✅ View Reports
- ❌ Cannot manage other institutions

### Faculty
Teaching staff permissions:
- ✅ Enter Marks
- ✅ Mark Attendance
- ✅ View Reports
- ❌ Cannot delete or modify students

### Data Entry
Basic data entry:
- ✅ Enter basic information
- ❌ Limited access to critical operations

---

## 📝 How to Create More Admins

### Option 1: Using the Script
```bash
cd backend
python create_admin.py
```

### Option 2: Manually in Database
1. Go to Supabase Dashboard
2. Navigate to `admin_users` table
3. Insert new row with:
   - `email`: Admin email
   - `password_hash`: Use bcrypt to hash password
   - `full_name`: Admin name
   - `role`: `super_admin`, `institution_admin`, `faculty`, or `data_entry`
   - `permissions`: JSON object with permissions
   - `is_active`: `true`

### Option 3: API Endpoint (requires super admin token)
```bash
POST http://localhost:8000/admin/register
Authorization: Bearer <super_admin_token>
Body: {
  "email": "newadmin@example.com",
  "password": "SecurePassword123",
  "full_name": "New Admin",
  "role": "institution_admin"
}
```

---

## 🧪 Testing Admin Login

### Step 1: Refresh CMS Page
Go to: http://localhost:3001

### Step 2: Enter Admin Credentials
- Email: `admin@bharatace.com`
- Password: `Admin@123456`

### Step 3: Expected Behavior
- ✅ Shows "Welcome Super Admin! Logging in..."
- ✅ Redirects to dashboard at `/dashboard`
- ✅ Can see analytics with real student data
- ✅ Can navigate all sidebar modules

### Step 4: Verify Token
Open browser DevTools → Application → Session Storage
- Should see `admin_token` with JWT value
- Should see `bharatace_authenticated` = "true"

---

## 🐛 Troubleshooting

### "Invalid admin credentials"
- Check if admin exists in `admin_users` table
- Verify password is `Admin@123456`
- Ensure `is_active` is `true`

### "Connection error"
- Ensure backend is running on port 8000
- Check backend terminal for errors
- Verify `/admin/login` endpoint is registered

### Dashboard shows empty
- This is expected if no data yet
- Analytics will populate as you add students/marks/attendance
- Backend endpoints are ready

### Token expired
- JWT tokens expire after 24 hours
- Just login again to get new token

---

## 🎉 Ready to Use!

Your CMS is now properly configured with admin authentication. You can:

1. **Login**: http://localhost:3001
2. **View Dashboard**: See student analytics
3. **Navigate Modules**: Use sidebar (Students, Marks, etc.)
4. **Manage Data**: Full CRUD access with admin permissions

Next step: Build the Student Management module UI! 🚀
