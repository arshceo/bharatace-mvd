"use client";

import { useState, FormEvent } from "react";
import toast from "react-hot-toast";

interface LoginModalProps {
  onLogin: () => void;
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    console.log('🔐 Attempting login with:', email);

    try {
      // Call backend ADMIN login API
      const response = await fetch("http://localhost:8000/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        // Store admin token and auth status
        sessionStorage.setItem("admin_token", data.access_token);
        sessionStorage.setItem("bharatace_authenticated", "true");
        
        console.log('✅ Login successful! Token saved to sessionStorage');
        console.log('✅ You can now access all CMS pages');
        console.log('📊 Caching system is active - pages will load instantly');
        
        toast.success(`Welcome ${data.admin?.full_name || "Admin"}! Logging in...`);
        onLogin();
      } else {
        toast.error(data.detail || "Invalid admin credentials. Please try again.");
        setPassword("");
      }
    } catch (error) {
      console.error("Login error:", error);
      toast.error("Connection error. Please ensure the backend is running.");
      setPassword("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        {/* Logo/Icon */}
        <div className="flex justify-center mb-6">
          <div className="bg-indigo-100 dark:bg-indigo-900 p-4 rounded-full">
            <svg
              className="w-12 h-12 text-indigo-600 dark:text-indigo-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-2">
          BharatAce CMS
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
          Admin Authentication Required
        </p>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !password || !email}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Verifying...
              </>
            ) : (
              <>
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                  />
                </svg>
                Sign In
              </>
            )}
          </button>
        </form>

        {/* Admin credentials hint */}
        <div className="mt-6 p-4 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-200 dark:border-amber-800">
          <p className="text-xs text-amber-800 dark:text-amber-300 font-semibold mb-1">
            🔐 Admin Access Required
          </p>
          <p className="text-xs text-amber-700 dark:text-amber-400">
            Please create an admin account in the database or contact your system administrator for credentials.
          </p>
          <p className="text-xs text-amber-600 dark:text-amber-500 mt-2 italic">
            Note: This is the admin panel, not the student portal.
          </p>
        </div>
      </div>
    </div>
  );
}
