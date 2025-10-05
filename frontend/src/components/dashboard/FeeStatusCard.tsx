"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';

interface FeeData {
  total_amount: number;
  paid_amount: number;
  pending_amount: number;
  status: string;
  late_fee: number;
  due_date: string;
}

export default function FeeStatusCard() {
  const { token, user } = useAuth();
  const [feeData, setFeeData] = useState<FeeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeeStatus = async () => {
      if (!token || !user?.student_data?.id) {
        setLoading(false);
        return;
      }

      try {
        // Placeholder data
        setFeeData({
          total_amount: 50000,
          paid_amount: 48000,
          pending_amount: 2000,
          status: 'partial',
          late_fee: 0,
          due_date: '2025-11-15',
        });
      } catch (error) {
        console.error('Error fetching fee status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFeeStatus();
  }, [token, user]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'text-green-600 bg-green-50';
      case 'partial':
        return 'text-yellow-600 bg-yellow-50';
      case 'overdue':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'paid':
        return '✓ Paid';
      case 'partial':
        return '⏳ Partial';
      case 'overdue':
        return '⚠ Overdue';
      default:
        return 'Pending';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Fee Status
        </h3>
        {feeData && (
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(feeData.status)}`}>
            {getStatusText(feeData.status)}
          </span>
        )}
      </div>

      {feeData ? (
        <>
          <div className="mb-6">
            <div className="flex items-baseline justify-between mb-2">
              <div>
                <p className="text-sm text-gray-500">Pending</p>
                <span className="text-4xl font-bold text-gray-900">₹{feeData.pending_amount.toLocaleString()}</span>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Total</p>
                <span className="text-xl font-semibold text-gray-600">₹{feeData.total_amount.toLocaleString()}</span>
              </div>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500"
                style={{ width: `${(feeData.paid_amount / feeData.total_amount) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-gray-100">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Paid Amount</span>
              <span className="text-sm font-semibold text-green-600">₹{feeData.paid_amount.toLocaleString()}</span>
            </div>
            
            {feeData.late_fee > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Late Fee</span>
                <span className="text-sm font-semibold text-red-600">₹{feeData.late_fee.toLocaleString()}</span>
              </div>
            )}

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Due Date</span>
              <span className="text-sm font-semibold text-gray-900">
                {new Date(feeData.due_date).toLocaleDateString('en-IN', { 
                  year: 'numeric', 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>

          {feeData.pending_amount > 1000 && (
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-xs text-yellow-700">
                <strong>⚠ Important:</strong> Clear fees soon to avoid late charges and exam restrictions
              </p>
            </div>
          )}

          {feeData.pending_amount <= 1000 && feeData.status !== 'paid' && (
            <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-xs text-green-700">
                <strong>✓ Eligible for Exams:</strong> Balance is below ₹1,000
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <svg className="h-12 w-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">No fee data available</p>
        </div>
      )}
    </div>
  );
}
