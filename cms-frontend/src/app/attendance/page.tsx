"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import { students, attendance as attendanceApi } from '@/lib/api';
import { Plus, Search, Calendar, CheckCircle, XCircle, X } from 'lucide-react';

interface Student {
  id: string;
  full_name?: string;
  first_name?: string;
  last_name?: string;
  enrollment_number?: string;
  roll_number?: string;
  student_id?: string;
  department?: string;
  branch?: string;
  course?: string;
  semester: number;
}

interface Attendance {
  id: string;
  student_id: string;
  date: string;
  status: 'present' | 'absent' | 'late';
  subject: string;
  remarks?: string;
}

export default function AttendancePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [attendanceData, setAttendanceData] = useState<Attendance[]>([]);
  const [studentsData, setStudentsData] = useState<Student[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [filterBranch, setFilterBranch] = useState('all');
  const [filterSemester, setFilterSemester] = useState('all');
  const [showBulkMarkModal, setShowBulkMarkModal] = useState(false);
  const [bulkAttendance, setBulkAttendance] = useState<Record<string, 'present' | 'absent' | 'late'>>({});

  useEffect(() => {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [attendanceRes, studentsRes] = await Promise.all([
        attendanceApi.getAll(),
        students.getAll(),
      ]);
      // Backend returns {attendance: [...]} and {students: [...]}
      const attendanceData = attendanceRes.data.attendance || attendanceRes.data || [];
      const studentsData = studentsRes.data.students || studentsRes.data || [];
      setAttendanceData(Array.isArray(attendanceData) ? attendanceData : []);
      setStudentsData(Array.isArray(studentsData) ? studentsData : []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setAttendanceData([]);
      setStudentsData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkMark = async () => {
    try {
      const records = Object.entries(bulkAttendance).map(([student_id, status]) => ({
        student_id,
        date: selectedDate,
        status,
        subject: 'General',
      }));

      await attendanceApi.create({ records });
      setShowBulkMarkModal(false);
      setBulkAttendance({});
      fetchData();
    } catch (error) {
      console.error('Error marking attendance:', error);
      alert('Failed to mark attendance');
    }
  };

  const getAttendanceStats = (studentId: string) => {
    const studentAttendance = attendanceData.filter(a => a.student_id === studentId);
    const totalDays = studentAttendance.length;
    const presentDays = studentAttendance.filter(a => a.status === 'present').length;
    const percentage = totalDays > 0 ? (presentDays / totalDays) * 100 : 0;
    return { totalDays, presentDays, percentage };
  };

  const filteredStudents = studentsData.filter((student) => {
    const branch = student.branch || student.department || '';
    const matchesBranch = filterBranch === 'all' || branch === filterBranch;
    const matchesSemester = filterSemester === 'all' || student.semester === parseInt(filterSemester);
    return matchesBranch && matchesSemester;
  });

  const branches = ['CSE', 'ECE', 'ME', 'CE', 'EE'];
  const semesters = [1, 2, 3, 4, 5, 6, 7, 8];

  if (loading) {
    return (
      <SidebarLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Attendance Management
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Mark and track student attendance
            </p>
          </div>
          <button
            onClick={() => setShowBulkMarkModal(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            Mark Attendance
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Date</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <select
              value={filterBranch}
              onChange={(e) => setFilterBranch(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Branches</option>
              {branches.map((branch) => (
                <option key={branch} value={branch}>{branch}</option>
              ))}
            </select>
            <select
              value={filterSemester}
              onChange={(e) => setFilterSemester(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Semesters</option>
              {semesters.map((sem) => (
                <option key={sem} value={sem}>Semester {sem}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Attendance Overview */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Enrollment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Branch</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Semester</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total Days</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Present</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Percentage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredStudents.map((student) => {
                  const stats = getAttendanceStats(student.id);
                  return (
                    <tr key={student.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="h-10 w-10 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center">
                            <span className="text-indigo-600 dark:text-indigo-400 font-medium">
                              {(student.full_name || `${student.first_name || ''} ${student.last_name || ''}`.trim() || 'U').charAt(0)}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {student.full_name || `${student.first_name || ''} ${student.last_name || ''}`.trim() || 'Unknown'}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {student.enrollment_number || student.roll_number || student.student_id || 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {student.branch || student.department || student.course || 'N/A'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {student.semester || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {stats.totalDays}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {stats.presentDays}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <span className={`text-sm font-medium ${
                            stats.percentage >= 75 ? 'text-green-600' :
                            stats.percentage >= 60 ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {stats.percentage.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Bulk Mark Modal */}
        {showBulkMarkModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Mark Attendance - {new Date(selectedDate).toLocaleDateString()}
                  </h2>
                  <button onClick={() => setShowBulkMarkModal(false)}>
                    <X className="w-6 h-6" />
                  </button>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {filteredStudents.map((student) => (
                    <div key={student.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {student.full_name || `${student.first_name || ''} ${student.last_name || ''}`.trim() || 'Unknown'}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {student.enrollment_number || student.roll_number || 'N/A'}
                        </p>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setBulkAttendance({ ...bulkAttendance, [student.id]: 'present' })}
                          className={`px-3 py-1 rounded-lg ${
                            bulkAttendance[student.id] === 'present'
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-300'
                          }`}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setBulkAttendance({ ...bulkAttendance, [student.id]: 'absent' })}
                          className={`px-3 py-1 rounded-lg ${
                            bulkAttendance[student.id] === 'absent'
                              ? 'bg-red-600 text-white'
                              : 'bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-300'
                          }`}
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setShowBulkMarkModal(false)}
                    className="px-4 py-2 border rounded-lg text-gray-700 dark:text-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleBulkMark}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                  >
                    Save Attendance
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </SidebarLayout>
  );
}
