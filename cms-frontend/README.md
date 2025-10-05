# BharatAce CMS Frontend

A modern, responsive Content Management System built with Next.js 14, TypeScript, and Tailwind CSS for managing the BharatAce AI Campus Assistant knowledge base.

## 🚀 Features

- **Secure Authentication**: Password-protected admin access
- **Knowledge Management**: Add and view knowledge base items
- **Real-time Updates**: Automatic refresh after adding new content
- **Responsive Design**: Beautiful UI that works on all devices
- **Dark Mode Support**: Automatic dark mode based on system preferences
- **Toast Notifications**: User-friendly feedback for all actions
- **Category-based Organization**: Organize knowledge by categories

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js**: Version 18.x or higher ([Download Node.js](https://nodejs.org/))
- **npm**: Comes with Node.js (or use yarn/pnpm)
- **Backend API**: The FastAPI backend must be running on `http://localhost:8000`

## 🛠️ Installation & Setup

### Step 1: Install Dependencies

Navigate to the `cms-frontend` directory and install all required packages:

```powershell
cd "d:\React Projects\Bharatace_mvd\cms-frontend"
npm install
```

This will install all dependencies listed in `package.json`, including:
- Next.js 14.2.5
- React 18.3.1
- TypeScript 5.5.3
- Tailwind CSS 3.4.6
- Axios 1.7.2
- React Hot Toast 2.4.1

**Expected output**: You should see a progress bar and "added XXX packages" message.

### Step 2: Configure Environment Variables

Create a `.env.local` file from the example template:

```powershell
Copy-Item .env.local.example .env.local
```

**Edit the `.env.local` file** to configure your backend API URL:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important**: If your backend is running on a different port or host, update this value accordingly.

### Step 3: Verify Backend Connection

Before starting the frontend, ensure your FastAPI backend is running:

1. Open a **separate PowerShell terminal**
2. Navigate to the backend directory:
   ```powershell
   cd "d:\React Projects\Bharatace_mvd\backend"
   ```
3. Activate your Python environment and start the server:
   ```powershell
   uvicorn main:app --reload
   ```
4. Verify it's running by visiting: http://localhost:8000

### Step 4: Run the Development Server

Start the Next.js development server:

```powershell
npm run dev
```

**Expected output**:
```
> cms-frontend@1.0.0 dev
> next dev

   ▲ Next.js 14.2.5
   - Local:        http://localhost:3000
   - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

### Step 5: Access the Application

Open your browser and navigate to:

**http://localhost:3000**

You should see the **BharatAce CMS login screen**.

## 🔐 Default Credentials

For development/demo purposes, use the following password:

```
Password: BharatAceAdmin@2025
```

**Note**: This is a hardcoded password for the MVD. In production, implement proper authentication with database-backed user management.

## 📖 Usage Guide

### Adding Knowledge Items

1. **Log in** using the admin password
2. In the **left panel**, you'll see the "Add New Knowledge" form
3. Enter the following:
   - **Category**: A short category name (e.g., "Library", "Admission", "Courses")
   - **Content**: The detailed information content
4. Click **"Add Knowledge"**
5. You'll see a success toast notification, and the item appears in the right panel

### Viewing Knowledge Items

- All knowledge items are displayed in the **right panel** ("Current Knowledge")
- Items show:
  - **Category badge** (color-coded)
  - **Content text**
  - **Creation timestamp**
- The list auto-scrolls and includes a "Back to Top" button for easy navigation

### Logging Out

Click the **"Logout"** button in the top-right corner to end your session.

## 🏗️ Project Structure

```
cms-frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout with Toaster
│   │   ├── page.tsx           # Main CMS dashboard
│   │   └── globals.css        # Global styles & Tailwind directives
│   └── components/
│       ├── LoginModal.tsx     # Authentication modal
│       ├── AddKnowledgeForm.tsx  # Form to add knowledge
│       └── KnowledgeList.tsx  # Display knowledge items
├── public/                     # Static assets
├── .env.local.example         # Environment variables template
├── .gitignore                 # Git ignore rules
├── next.config.ts             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── postcss.config.mjs         # PostCSS configuration
├── package.json               # Project dependencies
└── README.md                  # This file
```

## 🎨 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.5 | React framework with App Router |
| React | 18.3.1 | UI library |
| TypeScript | 5.5.3 | Type safety |
| Tailwind CSS | 3.4.6 | Utility-first CSS framework |
| Axios | 1.7.2 | HTTP client for API calls |
| React Hot Toast | 2.4.1 | Toast notifications |

## 🔌 API Integration

The frontend communicates with the FastAPI backend using the following endpoints:

### POST `/knowledge`
Add a new knowledge item to the database.

**Request Body**:
```json
{
  "category": "Library",
  "content": "The central library is open from 8 AM to 10 PM on weekdays."
}
```

**Response**: `201 Created`
```json
{
  "id": "uuid-here",
  "category": "Library",
  "content": "The central library is open from 8 AM to 10 PM on weekdays.",
  "created_at": "2025-01-20T10:30:00Z"
}
```

### GET `/knowledge`
Retrieve all knowledge items from the database.

**Response**: `200 OK`
```json
[
  {
    "id": "uuid-1",
    "category": "Library",
    "content": "The central library is open from 8 AM to 10 PM on weekdays.",
    "created_at": "2025-01-20T10:30:00Z"
  },
  {
    "id": "uuid-2",
    "category": "Admission",
    "content": "Applications are open from June to August every year.",
    "created_at": "2025-01-20T11:00:00Z"
  }
]
```

## 🛠️ Available Scripts

```powershell
# Install all dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server (after build)
npm start

# Run ESLint for code quality
npm run lint
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"

**Symptoms**: Toast error saying "Failed to add knowledge" or "Failed to load knowledge"

**Solutions**:
1. Verify backend is running: http://localhost:8000
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Look for CORS errors in browser console (F12)
4. Ensure backend's CORS settings allow `http://localhost:3000`

### Issue: "Module not found" errors

**Symptoms**: TypeScript errors or import failures

**Solutions**:
```powershell
# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Issue: Port 3000 already in use

**Symptoms**: Error message "Port 3000 is already in use"

**Solutions**:
```powershell
# Use a different port
$env:PORT=3001; npm run dev

# Or kill the process using port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
```

### Issue: Dark mode not working

**Solution**: Dark mode is based on system preferences. Change your OS theme settings to test.

### Issue: Toast notifications not appearing

**Solution**: The `<Toaster />` component is in `layout.tsx`. Ensure you haven't modified or removed it.

## 🔒 Security Considerations

**⚠️ IMPORTANT FOR PRODUCTION**:

1. **Authentication**: Replace hardcoded password with proper authentication:
   - Use JWT tokens
   - Implement user database
   - Add password hashing (bcrypt)
   - Use environment variables for secrets

2. **API Security**: 
   - Add API authentication headers
   - Implement rate limiting
   - Use HTTPS in production

3. **Environment Variables**:
   - Never commit `.env.local` to version control
   - Use server-side environment variables for sensitive data

## 📦 Building for Production

To create an optimized production build:

```powershell
# Build the application
npm run build

# Start the production server
npm start
```

The optimized build will be created in the `.next` folder.

## 🌐 Deployment Options

### Vercel (Recommended)
1. Push your code to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy automatically

### Other Platforms
- **Netlify**: Use Next.js adapter
- **AWS Amplify**: Configure build settings
- **Docker**: Create Dockerfile with Node.js base image

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL |

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## 🎯 Next Steps & Enhancements

Consider these improvements for production:

- [ ] Add user authentication with database
- [ ] Implement knowledge item editing
- [ ] Add delete functionality with confirmation
- [ ] Include search and filter capabilities
- [ ] Add pagination for large datasets
- [ ] Implement file upload for bulk knowledge import
- [ ] Add analytics dashboard
- [ ] Include audit logs for changes
- [ ] Add role-based access control (RBAC)
- [ ] Implement data export functionality

## 🤝 Contributing

This is a Minimum Viable Demo (MVD). For production use:
1. Fork the repository
2. Create a feature branch
3. Implement proper authentication
4. Add comprehensive tests
5. Submit pull requests

## 📄 License

© 2025 BharatAce University. All rights reserved.

## 💬 Support

For issues or questions:
- Check the troubleshooting section above
- Review backend API logs at `http://localhost:8000/docs`
- Inspect browser console (F12) for client-side errors

---

**Quick Start Summary**:
```powershell
# 1. Install dependencies
npm install

# 2. Create environment file
Copy-Item .env.local.example .env.local

# 3. Ensure backend is running at http://localhost:8000

# 4. Run development server
npm run dev

# 5. Open http://localhost:3000 in your browser

# 6. Login with: BharatAceAdmin@2025
```

**You're all set! 🎉**
