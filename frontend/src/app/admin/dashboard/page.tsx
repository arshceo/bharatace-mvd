'use client'

import { useEffect, useState } from 'react'
import {
  Users,
  GraduationCap,
  BookOpen,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Calendar,
  Building2
} from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function AdminDashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (!token) return

    fetch('http://localhost:8000/admin/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setDashboardData(data)
        setLoading(false)
      })
      .catch(console.error)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    )
  }

  const stats = dashboardData?.stats || {}

  const statCards = [
    {
      title: 'Total Students',
      value: stats.total_students || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Total Faculty',
      value: stats.total_faculty || 0,
      icon: GraduationCap,
      color: 'bg-purple-500',
      change: '+5%'
    },
    {
      title: 'Avg CGPA',
      value: stats.average_cgpa?.toFixed(2) || '0.00',
      icon: TrendingUp,
      color: 'bg-green-500',
      change: '+0.3'
    },
    {
      title: 'Avg Attendance',
      value: `${stats.average_attendance?.toFixed(1) || 0}%`,
      icon: Calendar,
      color: 'bg-orange-500',
      change: '-2%'
    },
    {
      title: 'Fee Collection',
      value: `${stats.fee_collection_rate?.toFixed(1) || 0}%`,
      icon: DollarSign,
      color: 'bg-teal-500',
      change: '+8%'
    },
    {
      title: 'Active Events',
      value: stats.active_events || 0,
      icon: Calendar,
      color: 'bg-pink-500',
      change: 'This month'
    },
    {
      title: 'Total Subjects',
      value: stats.total_subjects || 0,
      icon: BookOpen,
      color: 'bg-indigo-500',
      change: 'All depts'
    },
    {
      title: 'Attendance Shortage',
      value: stats.students_with_shortage || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: '<75%'
    },
  ]

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']

  return (
    <div className="p-8 space-y-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome to BharatAce Admin Portal</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center text-white`}>
                <stat.icon size={24} />
              </div>
              <span className="text-sm text-green-600 font-medium">{stat.change}</span>
            </div>
            <h3 className="text-gray-600 text-sm font-medium">{stat.title}</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Distribution */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Student Distribution by Department</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={dashboardData?.department_distribution || []}
                dataKey="count"
                nameKey="department"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => `${entry.department}: ${entry.count}`}
              >
                {(dashboardData?.department_distribution || []).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* CGPA Distribution */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">CGPA Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dashboardData?.cgpa_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Enrollment Trend */}
        <div className="bg-white rounded-xl shadow-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Student Enrollment Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dashboardData?.enrollment_trend || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Usage Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 text-white">
        <h3 className="text-2xl font-bold mb-6">AI Agent Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-blue-100 text-sm">Total Queries</p>
            <p className="text-4xl font-bold mt-2">{dashboardData?.ai_usage?.total_queries || 0}</p>
          </div>
          <div>
            <p className="text-blue-100 text-sm">Queries Today</p>
            <p className="text-4xl font-bold mt-2">{dashboardData?.ai_usage?.queries_today || 0}</p>
          </div>
          <div>
            <p className="text-blue-100 text-sm">Avg Response Time</p>
            <p className="text-4xl font-bold mt-2">{dashboardData?.ai_usage?.average_response_time || 0}s</p>
          </div>
        </div>
        <div className="mt-6 bg-white/10 rounded-lg p-4">
          <p className="text-sm text-blue-100">Most Asked Category</p>
          <p className="text-xl font-semibold mt-1">{dashboardData?.ai_usage?.most_asked_category || 'N/A'}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors">
            <Users className="mx-auto mb-2 text-blue-600" size={24} />
            <p className="text-sm font-medium text-gray-900">Add Student</p>
          </button>
          <button className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 transition-colors">
            <GraduationCap className="mx-auto mb-2 text-purple-600" size={24} />
            <p className="text-sm font-medium text-gray-900">Add Faculty</p>
          </button>
          <button className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors">
            <BookOpen className="mx-auto mb-2 text-green-600" size={24} />
            <p className="text-sm font-medium text-gray-900">Enter Marks</p>
          </button>
          <button className="p-4 border-2 border-orange-200 rounded-lg hover:bg-orange-50 transition-colors">
            <Calendar className="mx-auto mb-2 text-orange-600" size={24} />
            <p className="text-sm font-medium text-gray-900">Mark Attendance</p>
          </button>
        </div>
      </div>
    </div>
  )
}
