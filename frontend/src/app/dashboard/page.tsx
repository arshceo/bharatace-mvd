"use client";

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import WelcomeCard from '@/components/dashboard/WelcomeCard';
import AttendanceCard from '@/components/dashboard/AttendanceCard';
import FeeStatusCard from '@/components/dashboard/FeeStatusCard';
import ChatInterface from '@/components/dashboard/ChatInterface';
import { useAuth } from '@/context/AuthContext';

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">BharatAce</h1>
                  <p className="text-xs text-gray-500">Super Smart AI Campus Assistant</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.student_data?.full_name || user?.email}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.student_data?.roll_number || 'Student'}
                  </p>
                </div>
                
                <button
                  onClick={logout}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all shadow-md hover:shadow-lg"
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <WelcomeCard />
          </div>

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            {/* Stats Cards */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
              <AttendanceCard />
              <FeeStatusCard />
              
              {/* Quick Stats Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Today's Schedule
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Data Structures</p>
                      <p className="text-xs text-gray-500">Room 301</p>
                    </div>
                    <span className="text-xs font-semibold text-blue-600">9:00 AM</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-indigo-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Algorithms Lab</p>
                      <p className="text-xs text-gray-500">Lab 2</p>
                    </div>
                    <span className="text-xs font-semibold text-indigo-600">11:00 AM</span>
                  </div>
                  <div className="text-center py-2">
                    <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                      View Full Timetable →
                    </button>
                  </div>
                </div>
              </div>

              {/* Library Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Library Books
                </h3>
                <div className="text-center py-4">
                  <p className="text-4xl font-bold text-gray-900">2/3</p>
                  <p className="text-sm text-gray-500 mt-1">Books Issued</p>
                  <div className="mt-4 space-y-2">
                    <div className="text-left p-2 bg-gray-50 rounded-lg">
                      <p className="text-xs font-medium text-gray-900">Introduction to Algorithms</p>
                      <p className="text-xs text-gray-500">Due: Oct 20, 2025</p>
                    </div>
                    <div className="text-left p-2 bg-gray-50 rounded-lg">
                      <p className="text-xs font-medium text-gray-900">Database Systems</p>
                      <p className="text-xs text-gray-500">Due: Oct 25, 2025</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Chat Interface */}
            <div className="lg:col-span-1">
              <ChatInterface />
            </div>
          </div>

          {/* Upcoming Events */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Upcoming Events
              </h3>
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                View All →
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-2">
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded">Workshop</span>
                  <span className="text-xs text-gray-500">Oct 15</span>
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">AI & Machine Learning</h4>
                <p className="text-xs text-gray-600 mb-2">Learn the basics of ML with hands-on projects</p>
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                  Register →
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-2">
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">Competition</span>
                  <span className="text-xs text-gray-500">Oct 20</span>
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">Hackathon 2025</h4>
                <p className="text-xs text-gray-600 mb-2">24-hour coding challenge with prizes</p>
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                  Register →
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">Seminar</span>
                  <span className="text-xs text-gray-500">Oct 25</span>
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">Career Guidance</h4>
                <p className="text-xs text-gray-600 mb-2">Industry experts sharing career insights</p>
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                  Register →
                </button>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500">
              © 2025 BharatAce. Your personalized AI campus assistant powered by advanced AI.
            </p>
          </div>
        </footer>
      </div>
    </ProtectedRoute>
  );
}
