# 🔴 CRITICAL: YOU MUST LOGIN FIRST!

## The Problem
You're seeing "Network Error" because **you haven't logged in yet**. The API requires authentication.

## The Solution (30 seconds)

### Step 1: Open Login Page
Go to: **http://localhost:3001**

### Step 2: Login with These Credentials
```
Email: admin@bharatace.com
Password: Admin@123456
```

### Step 3: Verify Login
After clicking "Login", you should:
1. ✅ See a redirect to `/dashboard`
2. ✅ See green "✓ Caching active" messages in console
3. ✅ Be able to navigate to any page (Marks, Fees, Students, etc.)

## Why This Happens
- Every API call requires a JWT token
- Token is stored in `sessionStorage` after login
- Without token → Network Error
- With token → Everything works ✅

## Verify Backend is Running
```powershell
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

## Test Login Directly (PowerShell)
```powershell
$body = @{
    email = "admin@bharatace.com"
    password = "Admin@123456"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/admin/login" -Method POST -Body $body -ContentType "application/json"
$response.Content
```
Should return a token starting with `{"access_token":"eyJ...`

## After Login Works
All pages will:
- ✅ Load instantly (caching works)
- ✅ Show real data from database
- ✅ No more Network Errors
- ✅ Full CRUD operations work

---

**TL;DR: Just open http://localhost:3001 and login. That's it!**
