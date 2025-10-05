# BharatAce MVD - Multi-Tenant AI-Powered Educational Platform

## 🎓 Overview
BharatAce MVD is a comprehensive, production-ready educational management platform featuring:
- **AI-Powered Student Assistant** - RAG-based intelligent query system using Google Gemini
- **Student Portal** - Modern Next.js 15 + React 19 interface
- **CMS Admin Panel** - Complete management dashboard for administrators
- **FastAPI Backend** - High-performance API with 40+ endpoints
- **Multi-tenant Architecture** - Scalable for multiple educational institutions

## 🚀 Features

### Student Portal (Port 3000)
- ✅ AI chatbot for academic queries
- ✅ Marks and CGPA tracking
- ✅ Attendance management
- ✅ Library book loans
- ✅ Event information
- ✅ Real-time notifications

### CMS Admin Panel (Port 3001)
- ✅ Analytics dashboard with charts
- ✅ Student management (CRUD)
- ✅ Marks management
- ✅ Attendance tracking
- ✅ Fee collection
- ✅ Subject management
- ✅ Event scheduling
- ✅ Library management
- ✅ System settings

### Backend API (Port 8000)
- ✅ 40+ REST endpoints
- ✅ JWT authentication (Student + Admin)
- ✅ Role-based access control
- ✅ Supabase integration
- ✅ AI agent with 16 specialized tools
- ✅ RAG knowledge base with 11 documents
- ✅ Real-time data processing

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15.1.4
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

### Backend
- **Framework**: FastAPI
- **AI**: Google Gemini (LLM + Embeddings)
- **Vector Store**: LlamaIndex
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT tokens with bcrypt
- **Tools**: 16 specialized AI tools

### Database
- **Platform**: Supabase
- **Tables**: students, marks, attendance, fees, subjects, events, library_books, book_loans, admin_users, knowledge_base

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- Google AI API key

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

Create `.env` file in backend/:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret
GOOGLE_API_KEY=your_gemini_api_key
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Run backend:
```bash
uvicorn main:app --reload
```

### Student Portal Setup
```bash
cd frontend
npm install
npm run dev
```

### CMS Frontend Setup
```bash
cd cms-frontend
npm install
npm run dev
```

## 🔐 Default Credentials

### Student Portal
- Email: `sneha.patel@bharatace.edu.in`
- Password: `SecurePass@2024`

### CMS Admin Panel
- Email: `admin@bharatace.com`
- Password: `Admin@123456`

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/login` - Student login
- `POST /admin/login` - Admin login
- `GET /auth/me` - Get current user
- `GET /admin/me` - Get current admin

### Student Endpoints
- `GET /students` - List all students
- `GET /students/{id}` - Get student details
- `POST /students` - Create student
- `PUT /students/{id}` - Update student
- `DELETE /students/{id}` - Delete student

### Analytics Endpoints
- `GET /admin/analytics/dashboard` - Dashboard statistics
- `GET /admin/analytics/performance` - Student performance
- `GET /admin/analytics/attendance-trends` - Attendance trends
- `GET /admin/analytics/fee-collection` - Fee collection stats

### AI Agent Endpoint
- `POST /ask` - Ask AI assistant a question

## 🏗️ Project Structure
```
bharatace-mvd/
├── backend/
│   ├── api/
│   │   ├── admin_auth.py
│   │   ├── admin_dashboard.py
│   │   ├── admin_routes.py
│   │   └── auth_routes.py
│   ├── admin_models/
│   │   ├── __init__.py
│   │   └── admin.py
│   ├── tools/
│   │   ├── marks_tool.py
│   │   ├── attendance_tool.py
│   │   ├── library_tool.py
│   │   └── events_tool.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── smart_agent.py
│   └── requirements.txt
├── frontend/ (Student Portal)
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── next.config.ts
├── cms-frontend/ (Admin Panel)
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── students/
│   │   │   ├── marks/
│   │   │   ├── attendance/
│   │   │   ├── fees/
│   │   │   ├── subjects/
│   │   │   ├── events/
│   │   │   ├── library/
│   │   │   └── settings/
│   │   ├── components/
│   │   │   ├── LoginModal.tsx
│   │   │   └── SidebarLayout.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── package.json
│   └── next.config.ts
└── README.md
```

## 🚀 Deployment

### Backend (Railway/Render)
1. Set environment variables
2. Deploy from GitHub
3. Update CORS_ORIGINS with production URLs

### Frontend (Vercel)
1. Connect GitHub repository
2. Set NEXT_PUBLIC_API_URL to backend URL
3. Deploy

## 🔧 Development

### Create Admin User
```bash
cd backend
python create_admin.py
```

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 📊 AI Agent Capabilities
- Calculate CGPA and grades
- Retrieve student marks
- Check attendance records
- Query library book loans
- Get upcoming events
- Search knowledge base
- Provide academic guidance

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License
This project is proprietary and confidential.

## 👥 Authors
- **BharatAce Team** - *Initial work*

## 🙏 Acknowledgments
- Google Gemini AI for LLM capabilities
- Supabase for database infrastructure
- Next.js team for the amazing framework
- FastAPI for the high-performance backend
