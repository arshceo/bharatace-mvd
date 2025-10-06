# CMS Troubleshooting Guide

## ❌ Current Issue: "Network Error" when loading pages

### 🔍 Root Cause
The error "Network Error" in the marks page means the frontend **cannot communicate with the backend**. Here are the most common reasons:

### ✅ Solution Steps (Try in order)

#### **Step 1: Are you logged in?**
1. Open http://localhost:3001 in your browser
2. You should see a **login modal**
3. Enter credentials:
   - **Email**: `admin@bharatace.com` (or whatever admin email you have)
   - **Password**: `admin123` (or your admin password)
4. Click "Login"

**If you don't have admin credentials**, you need to create one in the database first.

#### **Step 2: Check if backend is running**
Open a new PowerShell terminal and run:
```powershell
curl http://localhost:8000/health
```

**Expected output:**
```json
{"status":"healthy"...}
```

**If it fails**: Backend is not running! Start it:
```powershell
cd "d:\React Projects\Bharatace_mvd\backend"
uvicorn main:app --reload
```

#### **Step 3: Check browser console**
1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Look for errors like:
   - `401 Unauthorized` → You're not logged in or token expired
   - `CORS error` → Backend CORS issue
   - `Network Error` → Backend not running or wrong URL
   - `500 Internal Server Error` → Backend has a bug

#### **Step 4: Verify token exists**
In browser console, run:
```javascript
console.log('Token:', sessionStorage.getItem('admin_token'));
console.log('Authenticated:', sessionStorage.getItem('bharatace_authenticated'));
```

**Expected output:**
```
Token: eyJhbGciOiJIUzI1NiIs... (long string)
Authenticated: true
```

**If null/empty**: You're not logged in! Go to step 1.

#### **Step 5: Test backend endpoint directly**
In PowerShell:
```powershell
# Replace YOUR_TOKEN with actual token from sessionStorage
$token = "YOUR_TOKEN_HERE"
$headers = @{Authorization="Bearer $token"}
Invoke-WebRequest -Uri "http://localhost:8000/admin/marks" -Headers $headers
```

**Expected**: Should return marks data or empty array
**If 401**: Token is invalid/expired - log in again
**If 500**: Backend error - check backend terminal logs

### 🎯 Quick Fix Commands

**Restart everything:**
```powershell
# Terminal 1 - Backend
cd "d:\React Projects\Bharatace_mvd\backend"
uvicorn main:app --reload

# Terminal 2 - Frontend  
cd "d:\React Projects\Bharatace_mvd\cms-frontend"
npm run dev
```

**Clear session and re-login:**
1. Open browser console (F12)
2. Run:
```javascript
sessionStorage.clear();
location.reload();
```
3. Log in again

### 📊 What Each Page Should Show

#### ✅ **When Logged In & Backend Running:**
- Students: Shows student count (may be 0 if no data)
- Marks: Shows marks count (may be 0 if no data)
- Fees: Shows fees count (may be 0 if no data)
- Subjects: Shows subjects count (may be 0 if no data)

#### ⚠️ **When NOT Logged In:**
- All pages redirect to login
- OR show "Authentication Required"

#### ❌ **When Backend is Down:**
- Pages show "Network Error"
- Red error box with troubleshooting steps

### 🔧 Common Issues & Fixes

| Issue | Symptoms | Fix |
|-------|----------|-----|
| **Not logged in** | Immediate redirect to home | Log in at http://localhost:3001 |
| **Token expired** | 401 errors in console | Clear session & log in again |
| **Backend down** | Network errors | Start backend with `uvicorn main:app --reload` |
| **Wrong port** | Connection refused | Backend MUST be on port 8000 |
| **No data in DB** | Count shows 0 | Normal for fresh install, add data via UI |

### 📝 How to Create Admin User (if needed)

If you don't have admin credentials, you need to add one to the database:

1. Open Supabase dashboard
2. Go to **Table Editor** → `admins` table
3. Insert new row:
   ```
   id: (auto-generated UUID)
   email: admin@bharatace.com
   full_name: Admin User
   role: admin
   created_at: (auto-generated)
   ```
4. Set password using Supabase Auth

OR use the backend API (if it has a signup endpoint).

### 🎨 Visual Indicators

The pages now show helpful messages:

- 🔵 **Blue spinner** = Loading data (first time)
- ✅ **Green checkmark** = Caching active, data loaded
- ⚠️ **Amber info** = No data in database yet (normal)
- ❌ **Red error** = Something wrong, see troubleshooting

### 🚀 Next Steps After Fixing

Once you can log in and see data (or see "0 records"):

1. **Add test data** via the UI (Add Student, Add Mark, etc.)
2. **Test caching** - Navigate between pages, notice instant loads
3. **Expand pages** - Add full CRUD to Marks/Fees/Subjects pages
4. **Add charts** - Visualize data with Chart.js

---

**Need Help?**
Check the browser console (F12) and backend terminal for detailed error messages!
