"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';

interface BookLoan {
  id: string;
  book: {
    title: string;
    author: string;
  };
  issue_date: string;
  due_date: string;
  return_date: string | null;
  status: string;
}

export default function LibraryCard() {
  const { token, user } = useAuth();
  const [loans, setLoans] = useState<BookLoan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBookLoans = async () => {
      if (!token || !user?.student_data?.id) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.library.getLoans();
        const data = response.data;
        
        // Backend returns { loans: [...], active_count: ..., total_count: ... }
        const allLoans = Array.isArray(data) ? data : (data.loans || []);
        
        // Filter active loans (not returned)
        const activeLoans = allLoans.filter((loan: BookLoan) => !loan.return_date);
        setLoans(activeLoans);
      } catch (error) {
        console.error('Error fetching book loans:', error);
        setLoans([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBookLoans();
  }, [token, user]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const maxBooks = 3;
  const issuedCount = loans.length;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        Library Books
      </h3>
      
      <div className="text-center py-4">
        <p className="text-4xl font-bold text-gray-900">{issuedCount}/{maxBooks}</p>
        <p className="text-sm text-gray-500 mt-1">Books Issued</p>
        
        {loans.length > 0 ? (
          <div className="mt-4 space-y-2">
            {loans.map((loan) => {
              const dueDate = new Date(loan.due_date);
              const today = new Date();
              const isOverdue = dueDate < today;
              
              return (
                <div key={loan.id} className={`text-left p-2 rounded-lg ${isOverdue ? 'bg-red-50' : 'bg-gray-50'}`}>
                  <p className="text-xs font-medium text-gray-900 truncate">{loan.book.title}</p>
                  <p className={`text-xs ${isOverdue ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                    Due: {dueDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    {isOverdue && ' (Overdue!)'}
                  </p>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">No books currently issued</p>
          </div>
        )}
      </div>
    </div>
  );
}
