# 🚀 BharatAce MVD - Quick Start Guide

## ⚡ TL;DR - Get Running in 2 Minutes

### Prerequisites
- ✅ Python 3.13 installed
- ✅ Node.js 18+ installed
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed (426 packages)

---

## 🎯 Start Both Servers

### Option 1: Two Separate Terminals (Recommended)

**Terminal 1 - Backend**:
```powershell
cd "d:\React Projects\Bharatace_mvd\backend"
uvicorn main:app --reload
```
Wait for: `✓ Application startup complete.`

**Terminal 2 - Frontend**:
```powershell
cd "d:\React Projects\Bharatace_mvd\cms-frontend"
npm run dev
```
Wait for: `✓ Ready in 3.8s`

### Option 2: PowerShell Script

Create `start-servers.ps1`:
```powershell
# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\React Projects\Bharatace_mvd\backend'; uvicorn main:app --reload"

# Wait 5 seconds for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\React Projects\Bharatace_mvd\cms-frontend'; npm run dev"
```

Run: `.\start-servers.ps1`

---

## 🌐 Access the Application

1. **Open Browser**: http://localhost:3000
2. **Login Password**: `BharatAceAdmin@2025`
3. **Add Knowledge**: Use the left panel form
4. **View Knowledge**: Items appear in right panel

---

## 🧪 Quick Test

```powershell
# Test Backend
curl http://localhost:8000

# Test Frontend
curl http://localhost:3000
```

Expected: Both return 200 OK

---

## 📋 Application URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Admin CMS Interface |
| Backend API | http://localhost:8000 | REST API Server |
| API Docs | http://localhost:8000/docs | Interactive API Documentation |
| Health Check | http://localhost:8000 | Server Status |

---

## 🎨 Using the CMS

### 1. Login
- Password: `BharatAceAdmin@2025`
- Click "Sign In"

### 2. Add Knowledge
**Left Panel - "Add New Knowledge"**:
- **Category**: Enter a category (e.g., "Library", "Courses", "Admission")
- **Content**: Enter the information content
- Click **"Add Knowledge"**
- ✅ Success toast appears
- 🔄 Right panel auto-updates

### 3. View Knowledge
**Right Panel - "Current Knowledge"**:
- All items listed with:
  - 🏷️ Color-coded category badge
  - 📝 Content text
  - 🕐 Timestamp

### 4. Test AI (Optional)
```powershell
curl -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"What are the library hours?\"}'
```

---

## 🛑 Stop Servers

Press `Ctrl+C` in each terminal window

---

## 🔍 Troubleshooting

### Backend won't start
```powershell
# Check if port 8000 is in use
Get-NetTCPConnection -LocalPort 8000

# Kill the process if needed
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

### Frontend won't start
```powershell
# Check if port 3000 is in use
Get-NetTCPConnection -LocalPort 3000

# Use a different port
$env:PORT=3001; npm run dev
```

### Can't connect to backend
1. Verify backend is running: http://localhost:8000
2. Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Check browser console (F12) for CORS errors

### Knowledge not appearing
1. Check backend terminal for errors
2. Open browser console (F12)
3. Verify network requests are succeeding (200 OK)

---

## 📁 Project Structure

```
Bharatace_mvd/
├── backend/          → FastAPI + AI (Port 8000)
├── cms-frontend/     → Next.js CMS (Port 3000)
└── PROJECT_COMPLETE.md → Full documentation
```

---

## 📚 Documentation

- **Frontend Guide**: `cms-frontend/README.md` (500+ lines)
- **Backend Guide**: `backend/README.md`
- **Complete Guide**: `PROJECT_COMPLETE.md`
- **API Docs**: http://localhost:8000/docs (when running)

---

## ✅ Health Check

**Backend**:
```powershell
curl http://localhost:8000
```
Expected Response:
```json
{
  "message": "BharatAce AI Campus Assistant API",
  "status": "operational",
  "version": "1.0.0"
}
```

**Frontend**:
- Visit http://localhost:3000
- Should see login modal

---

## 🎯 Common Tasks

### Add Sample Data
```powershell
# Using PowerShell
$body = @{
    category = "Library"
    content = "The central library is open from 8 AM to 10 PM on weekdays and 9 AM to 6 PM on weekends."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/knowledge" -Method Post -Body $body -ContentType "application/json"
```

### View All Knowledge
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/knowledge" -Method Get
```

### Ask AI a Question
```powershell
$question = @{
    question = "What are the library hours?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body $question -ContentType "application/json"
```

---

## 🔐 Environment Variables

### Backend (`.env`)
```env
SUPABASE_URL=https://gdltegmlnhmfitsfkzcc.supabase.co
SUPABASE_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 💡 Tips

1. **Auto-Reload**: Both servers support hot reload - changes appear instantly
2. **Dark Mode**: Automatically follows system theme preferences
3. **Session**: Login session persists in browser (sessionStorage)
4. **Responsive**: Works on mobile, tablet, and desktop
5. **Logs**: Check terminal output for debugging information

---

## 🚀 What's Running?

When both servers are started:

```
✅ Backend API          → Port 8000
✅ Supabase Connection  → Remote Database
✅ Google Gemini LLM    → AI Integration
✅ Vector Index         → Semantic Search
✅ Next.js Frontend     → Port 3000
✅ React Hot Reload     → Development Mode
✅ Tailwind CSS         → Styling System
```

---

## 📊 Current Status

- ✅ Backend: RUNNING
- ✅ Frontend: RUNNING
- ✅ Database: CONNECTED
- ✅ AI: INITIALIZED
- ✅ Integration: WORKING
- ✅ Zero Errors: CONFIRMED

---

## 🎉 You're All Set!

**Frontend**: http://localhost:3000  
**Password**: BharatAceAdmin@2025  
**Backend**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

Happy coding! 🚀
