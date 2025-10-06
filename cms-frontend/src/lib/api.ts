import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      sessionStorage.removeItem('admin_token');
      sessionStorage.removeItem('bharatace_authenticated');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// API Endpoints

// Authentication
export const auth = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
};

// Students
export const students = {
  getAll: () => api.get('/admin/students'),
  getById: (id: string) => api.get(`/admin/students/${id}`),
  create: (data: any) => api.post('/admin/students', data),
  update: (id: string, data: any) => api.put(`/admin/students/${id}`, data),
  delete: (id: string) => api.delete(`/admin/students/${id}`),
};

// Marks
export const marks = {
  getAll: () => api.get('/admin/marks'),
  getByStudent: (studentId: string) => api.get(`/admin/marks/student/${studentId}`),
  create: (data: any) => api.post('/admin/marks', data),
  update: (id: string, data: any) => api.put(`/admin/marks/${id}`, data),
  delete: (id: string) => api.delete(`/admin/marks/${id}`),
};

// Attendance
export const attendance = {
  getAll: () => api.get('/admin/attendance'),
  getByStudent: (studentId: string) => api.get(`/admin/attendance/student/${studentId}`),
  create: (data: any) => api.post('/admin/attendance', data),
  update: (id: string, data: any) => api.put(`/admin/attendance/${id}`, data),
  delete: (id: string) => api.delete(`/admin/attendance/${id}`),
};

// Fees
export const fees = {
  getAll: () => api.get('/admin/fees'),
  getByStudent: (studentId: string) => api.get(`/admin/fees/student/${studentId}`),
  create: (data: any) => api.post('/admin/fees', data),
  update: (id: string, data: any) => api.put(`/admin/fees/${id}`, data),
  recordPayment: (id: string, data: any) => api.post(`/admin/fees/${id}/payment`, data),
};

// Subjects
export const subjects = {
  getAll: () => api.get('/admin/subjects'),
  create: (data: any) => api.post('/admin/subjects', data),
  update: (id: string, data: any) => api.put(`/admin/subjects/${id}`, data),
  delete: (id: string) => api.delete(`/admin/subjects/${id}`),
};

// Events
export const events = {
  getAll: () => api.get('/admin/events'),
  getById: (id: string) => api.get(`/admin/events/${id}`),
  getParticipants: (id: string) => api.get(`/admin/events/${id}/participants`),
  create: (data: any) => api.post('/admin/events', data),
  update: (id: string, data: any) => api.put(`/admin/events/${id}`, data),
  delete: (id: string) => api.delete(`/admin/events/${id}`),
};

// Library
export const library = {
  getBooks: () => api.get('/admin/library/books'),
  getLoans: () => api.get('/admin/library/loans'),
  createBook: (data: any) => api.post('/admin/library/books', data),
  updateBook: (id: string, data: any) => api.put(`/admin/library/books/${id}`, data),
  deleteBook: (id: string) => api.delete(`/admin/library/books/${id}`),
};

// Knowledge Base
export const knowledge = {
  getAll: () => api.get('/knowledge'),
  create: (data: any) => api.post('/knowledge', data),
  update: (id: string, data: any) => api.put(`/knowledge/${id}`, data),
  delete: (id: string) => api.delete(`/knowledge/${id}`),
};

// Analytics & Reports
export const analytics = {
  getDashboardStats: () => api.get('/admin/analytics/dashboard'),
  getStudentPerformance: () => api.get('/admin/analytics/performance'),
  getAttendanceTrends: () => api.get('/admin/analytics/attendance-trends'),
  getFeeCollection: () => api.get('/admin/analytics/fee-collection'),
};

// Export unified API object
export default {
  auth,
  students,
  marks,
  attendance,
  fees,
  subjects,
  events,
  library,
  knowledge,
  analytics,
};
