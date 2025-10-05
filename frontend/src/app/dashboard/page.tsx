"use client";

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import WelcomeCard from '@/components/dashboard/WelcomeCard';
import AttendanceCard from '@/components/dashboard/AttendanceCard';
import FeeStatusCard from '@/components/dashboard/FeeStatusCard';
import TodayScheduleCard from '@/components/dashboard/TodayScheduleCard';
import LibraryCard from '@/components/dashboard/LibraryCard';
import UpcomingEventsCard from '@/components/dashboard/UpcomingEventsCard';
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
              <TodayScheduleCard />
              <LibraryCard />
            </div>

            {/* AI Chat Interface */}
            <div className="lg:col-span-1">
              <ChatInterface />
            </div>
          </div>

          {/* Upcoming Events */}
          <UpcomingEventsCard />
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
