"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';

interface AttendanceData {
  total_classes: number;
  attended: number;
  percentage: number;
  present: number;
  absent: number;
  late: number;
}

export default function AttendanceCard() {
  const { token, user } = useAuth();
  const [attendance, setAttendance] = useState<AttendanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttendance = async () => {
      if (!token || !user?.student_data?.id) {
        setLoading(false);
        return;
      }

      try {
        // This will be integrated with the AI agent later
        // For now, show a placeholder
        setAttendance({
          total_classes: 120,
          attended: 95,
          percentage: 79.2,
          present: 90,
          absent: 20,
          late: 5,
        });
      } catch (error) {
        console.error('Error fetching attendance:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAttendance();
  }, [token, user]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const getStatusColor = (percentage: number) => {
    if (percentage >= 85) return 'text-green-600 bg-green-50';
    if (percentage >= 75) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 85) return 'bg-green-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Attendance
        </h3>
        {attendance && (
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(attendance.percentage)}`}>
            {attendance.percentage >= 75 ? '✓ Good' : '⚠ Low'}
          </span>
        )}
      </div>

      {attendance ? (
        <>
          <div className="mb-6">
            <div className="flex items-baseline justify-between mb-2">
              <span className="text-4xl font-bold text-gray-900">{attendance.percentage.toFixed(1)}%</span>
              <span className="text-sm text-gray-500">{attendance.attended}/{attendance.total_classes} classes</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getProgressColor(attendance.percentage)}`}
                style={{ width: `${attendance.percentage}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{attendance.present}</p>
              <p className="text-xs text-gray-500 mt-1">Present</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{attendance.late}</p>
              <p className="text-xs text-gray-500 mt-1">Late</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{attendance.absent}</p>
              <p className="text-xs text-gray-500 mt-1">Absent</p>
            </div>
          </div>

          {attendance.percentage < 75 && (
            <div className="mt-4 p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-xs text-red-700">
                <strong>⚠ Shortage Alert:</strong> You need {Math.ceil((0.75 * attendance.total_classes - attendance.attended) / 0.25)} more classes to reach 75%
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <svg className="h-12 w-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p className="text-sm">No attendance data available</p>
        </div>
      )}
    </div>
  );
}
