import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Try 'auth_token' first (current standard), fallback to 'token' for backward compatibility
    const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear all auth data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Endpoints
export const apiClient = {
  // Auth
  auth: {
    login: (email: string, password: string) =>
      api.post('/auth/login', { email, password }),
    me: () => api.get('/auth/me'),
  },

  // Student data endpoints
  student: {
    getProfile: () => api.get('/student/profile'),
  },

  // Attendance endpoints - Direct database queries
  attendance: {
    getSummary: () => api.get('/student/attendance/summary'),
  },

  // Fees endpoints - Direct database queries
  fees: {
    getStatus: () => api.get('/student/fees/status'),
  },

  // Library endpoints - Direct database queries
  library: {
    getLoans: () => api.get('/student/library/loans'),
  },

  // Timetable endpoints - Direct database queries
  timetable: {
    getTodaySchedule: () => api.get('/student/timetable/today'),
  },

  // Marks endpoints - Direct database queries
  marks: {
    getSummary: () => api.get('/student/marks/summary'),
  },

  // Events endpoints - Direct database queries (public)
  events: {
    getUpcoming: () => api.get('/student/events/upcoming'),
    getMyEvents: () => api.get('/student/events/my-events'),
  },

  // AI Chat endpoint - For complex questions only
  chat: {
    ask: (query: string, conversationHistory?: Array<{role: string, content: string}>) => 
      api.post('/ask', { query, conversation_history: conversationHistory }),
  },
};

export default api;
