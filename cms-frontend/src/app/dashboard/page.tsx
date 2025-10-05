"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import api from '@/lib/api';
import {
  Users,
  GraduationCap,
  TrendingUp,
  DollarSign,
  AlertCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface DashboardStats {
  total_students: number;
  average_cgpa: number;
  attendance_rate: number;
  fee_collection_rate: number;
  total_fees: number;
  collected_fees: number;
}

interface PerformanceData {
  branch: string;
  average_cgpa: number;
  student_count: number;
}

interface AttendanceTrend {
  month: string;
  attendance_percentage: number;
  total_records: number;
}

interface FeeCollection {
  semester: number;
  total_fees: number;
  collected: number;
  pending: number;
  collection_rate: number;
}

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [performance, setPerformance] = useState<PerformanceData[]>([]);
  const [attendanceTrends, setAttendanceTrends] = useState<AttendanceTrend[]>([]);
  const [feeCollection, setFeeCollection] = useState<FeeCollection[]>([]);

  useEffect(() => {
    // Check authentication
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }

    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      console.log('🔍 Loading dashboard analytics...');
      console.log('🔑 Token:', sessionStorage.getItem('admin_token') ? 'Present' : 'Missing');
      console.log('🌐 API Base:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

      // Load all analytics data with individual error handling
      const [statsRes, perfRes, attendRes, feeRes] = await Promise.allSettled([
        api.analytics.getDashboardStats(),
        api.analytics.getStudentPerformance(),
        api.analytics.getAttendanceTrends(),
        api.analytics.getFeeCollection(),
      ]);

      // Extract data from settled promises
      if (statsRes.status === 'fulfilled') {
        console.log('✅ Dashboard stats loaded:', statsRes.value.data);
        setStats(statsRes.value.data);
      } else {
        console.error('❌ Stats error:', statsRes.reason);
        console.error('Response:', statsRes.reason.response?.data);
        console.error('Status:', statsRes.reason.response?.status);
        // Set default stats
        setStats({
          total_students: 0,
          average_cgpa: 0,
          attendance_rate: 0,
          fee_collection_rate: 0,
          total_fees: 0,
          collected_fees: 0
        });
      }

      if (perfRes.status === 'fulfilled') {
        console.log('✅ Performance data loaded');
        setPerformance(perfRes.value.data.performance || []);
      } else {
        console.error('❌ Performance error:', perfRes.reason.message);
      }

      if (attendRes.status === 'fulfilled') {
        console.log('✅ Attendance trends loaded');
        setAttendanceTrends(attendRes.value.data.trends || []);
      } else {
        console.error('❌ Attendance trends error:', attendRes.reason.message);
      }

      if (feeRes.status === 'fulfilled') {
        console.log('✅ Fee collection loaded');
        setFeeCollection(feeRes.value.data.collection || []);
      } else {
        console.error('❌ Fee collection error:', feeRes.reason.message);
      }
    } catch (error) {
      console.error('💥 Failed to load dashboard data:', error);
      // Set defaults so dashboard still renders
      setStats({
        total_students: 0,
        average_cgpa: 0,
        attendance_rate: 0,
        fee_collection_rate: 0,
        total_fees: 0,
        collected_fees: 0
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SidebarLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Welcome back! Here's what's happening with your institution.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Students"
            value={stats?.total_students || 0}
            icon={Users}
            color="bg-blue-500"
          />
          <StatsCard
            title="Average CGPA"
            value={stats?.average_cgpa.toFixed(2) || '0.00'}
            icon={GraduationCap}
            color="bg-green-500"
          />
          <StatsCard
            title="Attendance Rate"
            value={`${stats?.attendance_rate.toFixed(1)}%` || '0%'}
            icon={TrendingUp}
            color="bg-yellow-500"
          />
          <StatsCard
            title="Fee Collection"
            value={`${stats?.fee_collection_rate.toFixed(1)}%` || '0%'}
            icon={DollarSign}
            color="bg-purple-500"
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Branch Performance */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Branch-wise Performance
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={performance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="branch" />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="average_cgpa" fill="#4F46E5" name="Average CGPA" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Student Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Student Distribution by Branch
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={performance}
                  dataKey="student_count"
                  nameKey="branch"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {performance.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Attendance Trends */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Attendance Trends
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={attendanceTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="attendance_percentage"
                  stroke="#10B981"
                  name="Attendance %"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Fee Collection */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Fee Collection by Semester
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={feeCollection}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="semester" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="collected" fill="#10B981" name="Collected" stackId="a" />
                <Bar dataKey="pending" fill="#EF4444" name="Pending" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fee Summary */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Fee Collection Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Fees</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ₹{stats?.total_fees.toLocaleString('en-IN') || 0}
              </p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Collected</p>
              <p className="text-2xl font-bold text-green-600">
                ₹{stats?.collected_fees.toLocaleString('en-IN') || 0}
              </p>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
              <p className="text-2xl font-bold text-red-600">
                ₹{((stats?.total_fees || 0) - (stats?.collected_fees || 0)).toLocaleString('en-IN')}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => router.push('/students')}
              className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
            >
              <Users className="w-8 h-8 mx-auto mb-2 text-indigo-600" />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Manage Students
              </p>
            </button>
            <button
              onClick={() => router.push('/marks')}
              className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors"
            >
              <GraduationCap className="w-8 h-8 mx-auto mb-2 text-green-600" />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Enter Marks
              </p>
            </button>
            <button
              onClick={() => router.push('/attendance')}
              className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors"
            >
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Mark Attendance
              </p>
            </button>
            <button
              onClick={() => router.push('/fees')}
              className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors"
            >
              <DollarSign className="w-8 h-8 mx-auto mb-2 text-purple-600" />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Manage Fees
              </p>
            </button>
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: any;
  color: string;
}

function StatsCard({ title, value, icon: Icon, color }: StatsCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {value}
          </p>
        </div>
        <div className={`${color} rounded-lg p-3`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}
