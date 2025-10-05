'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  CalendarDays,
  DollarSign,
  Library,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Building2,
  ClipboardList
} from 'lucide-react'

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [adminInfo, setAdminInfo] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    // Check admin authentication
    const token = localStorage.getItem('admin_token')
    if (!token) {
      router.push('/admin/login')
      return
    }

    // Fetch admin info
    fetch('http://localhost:8000/admin/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setAdminInfo(data))
      .catch(() => {
        localStorage.removeItem('admin_token')
        router.push('/admin/login')
      })
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }

  const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/admin/dashboard' },
    { icon: Building2, label: 'Institutions', href: '/admin/institutions', permission: 'can_manage_institutions' },
    { icon: Users, label: 'Students', href: '/admin/students' },
    { icon: GraduationCap, label: 'Faculty', href: '/admin/faculty' },
    { icon: BookOpen, label: 'Subjects', href: '/admin/subjects' },
    { icon: ClipboardList, label: 'Marks Entry', href: '/admin/marks' },
    { icon: CalendarDays, label: 'Attendance', href: '/admin/attendance' },
    { icon: DollarSign, label: 'Fees', href: '/admin/fees' },
    { icon: Library, label: 'Library', href: '/admin/library' },
    { icon: FileText, label: 'Knowledge Base', href: '/admin/knowledge' },
    { icon: CalendarDays, label: 'Events', href: '/admin/events' },
    { icon: Settings, label: 'Settings', href: '/admin/settings' },
  ]

  // Filter menu items based on permissions
  const visibleMenuItems = adminInfo
    ? menuItems.filter(item => {
        if (!item.permission) return true
        return adminInfo.role === 'super_admin' || adminInfo.permissions?.[item.permission]
      })
    : menuItems

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-blue-900 to-blue-800 text-white transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 flex items-center justify-between border-b border-blue-700">
          {sidebarOpen && (
            <div>
              <h1 className="text-xl font-bold">BharatAce</h1>
              <p className="text-xs text-blue-200">Admin Portal</p>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-blue-700 rounded-lg"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {visibleMenuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-700 transition-colors group"
            >
              <item.icon size={20} />
              {sidebarOpen && <span className="text-sm">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* Admin Info */}
        {adminInfo && (
          <div className="p-4 border-t border-blue-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                {adminInfo.full_name?.charAt(0)}
              </div>
              {sidebarOpen && (
                <div className="flex-1">
                  <p className="text-sm font-medium">{adminInfo.full_name}</p>
                  <p className="text-xs text-blue-200">{adminInfo.role}</p>
                </div>
              )}
            </div>
            {sidebarOpen && (
              <button
                onClick={handleLogout}
                className="mt-3 w-full flex items-center justify-center gap-2 p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-sm"
              >
                <LogOut size={16} />
                Logout
              </button>
            )}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
