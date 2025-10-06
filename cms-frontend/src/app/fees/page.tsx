"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import { fees as feesApi } from '@/lib/api';
import { DollarSign, Search, Filter, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';

interface FeeRecord {
  id: string;
  student_id: string;
  student_name?: string;
  full_name?: string;
  first_name?: string;
  last_name?: string;
  roll_number?: string;
  enrollment_number?: string;
  semester: number;
  academic_year: string;
  total_amount: number;
  amount_paid: number;
  payment_status: 'pending' | 'partial' | 'paid' | 'overdue';
  due_date: string;
  payment_date?: string;
}

export default function FeesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [fees, setFees] = useState<FeeRecord[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
    fetchFees();
  }, [router]);

  const fetchFees = async () => {
    try {
      setLoading(true);
      const response = await feesApi.getAll();
      const feesData = response.data.fees || response.data || [];
      setFees(feesData);
    } catch (error) {
      console.error('Error fetching fees:', error);
      setFees([]);
    } finally {
      setLoading(false);
    }
  };

  const getStudentName = (fee: FeeRecord) => {
    return fee.student_name || fee.full_name || 
           `${fee.first_name || ''} ${fee.last_name || ''}`.trim() || 
           'Unknown Student';
  };

  const getStudentId = (fee: FeeRecord) => {
    return fee.roll_number || fee.enrollment_number || fee.student_id || 'N/A';
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      paid: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200', icon: CheckCircle },
      partial: { bg: 'bg-yellow-100 dark:bg-yellow-900', text: 'text-yellow-800 dark:text-yellow-200', icon: Clock },
      pending: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200', icon: AlertCircle },
      overdue: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-800 dark:text-red-200', icon: XCircle },
    };
    const badge = badges[status as keyof typeof badges] || badges.pending;
    const Icon = badge.icon;
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const filteredFees = fees.filter((fee) => {
    const studentName = getStudentName(fee).toLowerCase();
    const studentId = getStudentId(fee).toLowerCase();
    const matchesSearch = studentName.includes(searchQuery.toLowerCase()) || 
                         studentId.includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || fee.payment_status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const totalCollected = fees.reduce((sum, fee) => sum + (fee.amount_paid || 0), 0);
  const totalPending = fees.reduce((sum, fee) => sum + ((fee.total_amount || 0) - (fee.amount_paid || 0)), 0);

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
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Fees Management</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Total Records: {fees.length}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Collected</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  ₹{totalCollected.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-100 dark:bg-green-900 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Pending</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  ₹{totalPending.toLocaleString()}
                </p>
              </div>
              <div className="bg-red-100 dark:bg-red-900 p-3 rounded-lg">
                <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Collection Rate</p>
                <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                  {fees.length > 0 ? ((totalCollected / (totalCollected + totalPending)) * 100).toFixed(1) : 0}%
                </p>
              </div>
              <div className="bg-indigo-100 dark:bg-indigo-900 p-3 rounded-lg">
                <CheckCircle className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by student name or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Status</option>
                <option value="paid">Paid</option>
                <option value="partial">Partial</option>
                <option value="pending">Pending</option>
                <option value="overdue">Overdue</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Semester</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Paid</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Balance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Due Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredFees.map((fee) => {
                  const balance = (fee.total_amount || 0) - (fee.amount_paid || 0);
                  return (
                    <tr key={fee.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {getStudentName(fee)}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {getStudentId(fee)}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        Sem {fee.semester} - {fee.academic_year}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                        ₹{(fee.total_amount || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-green-600 dark:text-green-400">
                        ₹{(fee.amount_paid || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-red-600 dark:text-red-400">
                        ₹{balance.toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(fee.payment_status)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {fee.due_date ? new Date(fee.due_date).toLocaleDateString() : 'N/A'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {filteredFees.length === 0 && (
              <div className="text-center py-12">
                <DollarSign className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No fee records found</h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {searchQuery || filterStatus !== 'all' ? 'Try adjusting your filters' : 'No fee records available'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
}
