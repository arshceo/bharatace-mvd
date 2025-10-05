"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';

interface TimetableEntry {
  id: string;
  subject_name: string;
  room: string;
  start_time: string;
  end_time: string;
  day: string;
}

export default function TodayScheduleCard() {
  const { token, user } = useAuth();
  const [schedule, setSchedule] = useState<TimetableEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTodaySchedule = async () => {
      if (!token || !user?.student_data?.id) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.timetable.getTodaySchedule();
        setSchedule(response.data || []);
      } catch (error) {
        console.error('Error fetching today\'s schedule:', error);
        setSchedule([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTodaySchedule();
  }, [token, user]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Today's Schedule
      </h3>
      
      {schedule.length > 0 ? (
        <div className="space-y-3">
          {schedule.slice(0, 3).map((entry, index) => {
            const colors = ['bg-blue-50', 'bg-indigo-50', 'bg-purple-50'];
            const textColors = ['text-blue-600', 'text-indigo-600', 'text-purple-600'];
            
            return (
              <div key={entry.id} className={`flex items-center justify-between p-3 ${colors[index % 3]} rounded-lg`}>
                <div>
                  <p className="text-sm font-medium text-gray-900">{entry.subject_name}</p>
                  <p className="text-xs text-gray-500">{entry.room}</p>
                </div>
                <span className={`text-xs font-semibold ${textColors[index % 3]}`}>
                  {new Date(`2000-01-01T${entry.start_time}`).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                </span>
              </div>
            );
          })}
          {schedule.length > 3 && (
            <div className="text-center py-2">
              <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                View Full Timetable ({schedule.length} classes) →
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <svg className="h-12 w-12 mx-auto mb-2 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">No classes scheduled for today</p>
        </div>
      )}
    </div>
  );
}
