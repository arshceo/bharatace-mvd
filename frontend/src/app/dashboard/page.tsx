"use client";

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import WelcomeCard from '@/components/dashboard/WelcomeCard';
import AttendanceCard from '@/components/dashboard/AttendanceCard';
import FeeStatusCard from '@/components/dashboard/FeeStatusCard';
import TodayScheduleCard from '@/components/dashboard/TodayScheduleCard';
import LibraryCard from '@/components/dashboard/LibraryCard';
import UpcomingEventsCard from '@/components/dashboard/UpcomingEventsCard';
import MyEventsCard from '@/components/dashboard/MyEventsCard';
import ChatInterface from '@/components/dashboard/ChatInterface';
import { useAuth } from '@/context/AuthContext';

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-b from-[#0b1020] via-[#0b0f25] to-[#101225] text-white/90">
        {/* Subtle background glow */}
        <div className="pointer-events-none fixed inset-0 opacity-60">
          <div className="absolute -top-40 -left-32 h-96 w-96 rounded-full bg-fuchsia-600/20 blur-[120px]"></div>
          <div className="absolute -bottom-40 -right-32 h-96 w-96 rounded-full bg-indigo-600/20 blur-[120px]"></div>
        </div>

        {/* Header */}
        <header className="sticky top-0 inset-x-0 z-50 supports-[backdrop-filter]:bg-white/5 bg-white/10 border-white/5 border-b backdrop-blur-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 grid place-items-center shadow-lg shadow-fuchsia-500/20">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-xl font-semibold tracking-tight text-white">BharatAce</h1>
                  <p className="text-xs text-white/50">Super Smart AI Campus Assistant</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-white">
                    {user?.student_data?.full_name || user?.email}
                  </p>
                  <p className="text-xs text-white/50">
                    {user?.student_data?.roll_number || 'Student'}
                  </p>
                </div>
                
                <button
                  onClick={logout}
                  className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
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
        <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Page title */}
          <div className="mb-8">
            <h2 className="text-[28px] font-semibold text-white tracking-tight">Dashboard</h2>
            <p className="text-sm text-white/60">Your personalized academic overview</p>
          </div>

          {/* Welcome Section */}
          <div className="mb-8">
            <WelcomeCard />
          </div>

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
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

          {/* Events Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <MyEventsCard />
            <UpcomingEventsCard />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
