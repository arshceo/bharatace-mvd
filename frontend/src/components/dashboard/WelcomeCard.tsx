"use client";

import { useAuth } from '@/context/AuthContext';

export default function WelcomeCard() {
  const { user } = useAuth();

  const studentData = user?.student_data;

  return (
    <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl shadow-xl p-8 text-white">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="h-12 w-12 bg-blue-950 bg-opacity-20 rounded-full flex items-center justify-center backdrop-blur-sm">
              <svg className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-blue-100">Welcome back,</p>
              <h1 className="text-3xl font-bold">{studentData?.full_name || user?.email}</h1>
            </div>
          </div>

          {studentData && (
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="bg-blue-950 bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
                <p className="text-xs text-blue-100 mb-1">Roll Number</p>
                <p className="text-lg font-semibold">{studentData.roll_number}</p>
              </div>
              <div className="bg-blue-950 bg-opacity-10 rounded-lg p-3 backdrop-blur-sm">
                <p className="text-xs text-blue-100 mb-1">Semester</p>
                <p className="text-lg font-semibold">Semester {studentData.semester}</p>
              </div>
              <div className="bg-blue-950 bg-opacity-10 rounded-lg p-3 backdrop-blur-sm col-span-2">
                <p className="text-xs text-blue-100 mb-1">Department</p>
                <p className="text-lg font-semibold">{studentData.department}</p>
              </div>
            </div>
          )}
        </div>

        <div className="ml-4">
          <div className="h-20 w-20 bg-blue-950 bg-opacity-10 rounded-full flex items-center justify-center backdrop-blur-sm">
            <span className="text-4xl font-bold text-white">
              {studentData?.full_name?.charAt(0) || user?.email?.charAt(0).toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {studentData?.cgpa && (
        <div className="mt-6 pt-6 border-t border-white border-opacity-20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-100">Current CGPA</p>
              <p className="text-3xl font-bold mt-1">{studentData.cgpa.toFixed(2)}/10.0</p>
            </div>
            <div className="text-right">
              <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-950 bg-opacity-20 backdrop-blur-sm">
                <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {studentData.cgpa >= 9 ? 'Outstanding' : studentData.cgpa >= 8 ? 'Excellent' : studentData.cgpa >= 7 ? 'Good' : 'Fair'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
