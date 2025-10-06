"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import { subjects as subjectsApi } from '@/lib/api';
import { BookOpen, Search, Filter, Award } from 'lucide-react';

interface Subject {
  id: string;
  subject_code: string;
  subject_name: string;
  department: string;
  semester: number;
  credits: number;
  instructor_name?: string;
  instructor_email?: string;
  description?: string;
}

export default function SubjectsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [filterSemester, setFilterSemester] = useState('all');

  useEffect(() => {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
    fetchSubjects();
  }, [router]);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const response = await subjectsApi.getAll();
      const subjectsData = response.data.subjects || response.data || [];
      setSubjects(subjectsData);
    } catch (error) {
      console.error('Error fetching subjects:', error);
      setSubjects([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredSubjects = subjects.filter((subject) => {
    const matchesSearch = 
      subject.subject_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      subject.subject_code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      subject.instructor_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDepartment = filterDepartment === 'all' || subject.department === filterDepartment;
    const matchesSemester = filterSemester === 'all' || subject.semester.toString() === filterSemester;
    return matchesSearch && matchesDepartment && matchesSemester;
  });

  const departments = Array.from(new Set(subjects.map(s => s.department).filter(Boolean)));
  const semesters = Array.from(new Set(subjects.map(s => s.semester).filter(Boolean))).sort((a, b) => a - b);
  const totalCredits = filteredSubjects.reduce((sum, s) => sum + (s.credits || 0), 0);

  if (loading) {
    return (
      <SidebarLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Subjects</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Total Subjects: {subjects.length} | Total Credits: {totalCredits}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Subjects</p>
                <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{subjects.length}</p>
              </div>
              <div className="bg-indigo-100 dark:bg-indigo-900 p-3 rounded-lg">
                <BookOpen className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Departments</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">{departments.length}</p>
              </div>
              <div className="bg-green-100 dark:bg-green-900 p-3 rounded-lg">
                <Filter className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Avg Credits</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {subjects.length > 0 ? (totalCredits / subjects.length).toFixed(1) : 0}
                </p>
              </div>
              <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-lg">
                <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search subjects, code, or instructor..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <select
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Departments</option>
              {departments.map((dept) => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
            <select
              value={filterSemester}
              onChange={(e) => setFilterSemester(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Semesters</option>
              {semesters.map((sem) => (
                <option key={sem} value={sem.toString()}>Semester {sem}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Subject Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Semester</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Credits</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Instructor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredSubjects.map((subject) => (
                  <tr key={subject.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <span className="text-sm font-mono font-medium text-indigo-600 dark:text-indigo-400">
                        {subject.subject_code}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {subject.subject_name}
                        </div>
                        {subject.description && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {subject.description.length > 60 ? subject.description.substring(0, 60) + '...' : subject.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        {subject.department}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                      Sem {subject.semester}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Award className="w-4 h-4 text-yellow-500 mr-1" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {subject.credits}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {subject.instructor_name ? (
                        <div>
                          <div className="text-sm text-gray-900 dark:text-white">
                            {subject.instructor_name}
                          </div>
                          {subject.instructor_email && (
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {subject.instructor_email}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Not assigned</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredSubjects.length === 0 && (
              <div className="text-center py-12">
                <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No subjects found</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {searchQuery || filterDepartment !== 'all' || filterSemester !== 'all' 
                    ? 'Try adjusting your filters' 
                    : 'No subjects available'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
