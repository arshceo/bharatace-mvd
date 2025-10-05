"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

interface KnowledgeItem {
  id: string;
  category: string;
  content: string;
  created_at: string;
}

interface KnowledgeListProps {
  refreshTrigger: number;
}

export default function KnowledgeList({ refreshTrigger }: KnowledgeListProps) {
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchKnowledge = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.get<KnowledgeItem[]>(`${API_URL}/knowledge`);
      setKnowledgeItems(response.data);
    } catch (error) {
      const errorMessage = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : "An unexpected error occurred";
      
      setError(errorMessage);
      toast.error(`Failed to load knowledge: ${errorMessage}`);
      console.error("Error fetching knowledge:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data on component mount and when refreshTrigger changes
  useEffect(() => {
    fetchKnowledge();
  }, [refreshTrigger]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      courses: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
      admission: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
      facilities: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
      library: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
      campus_life: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300",
    };

    return colors[category.toLowerCase()] || "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300";
  };

  // Loading State
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg p-4 h-32"
          >
            <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/4 mb-3"></div>
            <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-full mb-2"></div>
            <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
          </div>
        ))}
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <svg
          className="w-12 h-12 text-red-500 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-red-800 dark:text-red-300 font-medium mb-2">
          Failed to load knowledge items
        </p>
        <p className="text-sm text-red-600 dark:text-red-400 mb-4">{error}</p>
        <button
          onClick={fetchKnowledge}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Empty State
  if (knowledgeItems.length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600 rounded-lg p-8 text-center">
        <svg
          className="w-16 h-16 text-gray-400 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No knowledge items yet
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Add your first knowledge item using the form on the left.
        </p>
      </div>
    );
  }

  // Knowledge Items List
  return (
    <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
      {knowledgeItems.map((item) => (
        <div
          key={item.id}
          className="bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
        >
          <div className="flex items-start justify-between mb-2">
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(
                item.category
              )}`}
            >
              {item.category}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {formatDate(item.created_at)}
            </span>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
            {item.content}
          </p>
        </div>
      ))}
      
      {/* Scroll to top button */}
      {knowledgeItems.length > 5 && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="w-full py-2 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium transition-colors duration-200"
        >
          ↑ Back to Top
        </button>
      )}
    </div>
  );
}
