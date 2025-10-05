"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import AddKnowledgeForm from '@/components/AddKnowledgeForm';
import KnowledgeList from '@/components/KnowledgeList';

export default function KnowledgePage() {
  const router = useRouter();
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  useEffect(() => {
    // Check authentication
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
  }, [router]);

  const triggerRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <SidebarLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Knowledge Base
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage the AI chatbot's knowledge base for student queries.
          </p>
        </div>

        {/* Add Knowledge Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Add New Knowledge
          </h2>
          <AddKnowledgeForm onSuccess={triggerRefresh} />
        </div>

        {/* Knowledge List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Existing Knowledge Base
          </h2>
          <KnowledgeList refreshTrigger={refreshTrigger} />
        </div>
      </div>
    </SidebarLayout>
  );
}
