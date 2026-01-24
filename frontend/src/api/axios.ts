import axios from 'axios';
import toast from 'react-hot-toast';

// In production: use empty string (relative URLs, nginx proxies /api to backend)
// In development: use localhost:8000
const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '');

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip 401 handling for login endpoint (let it show the error message)
    const isLoginRequest = originalRequest?.url?.includes('/api/auth/login');

    // Handle 401 Unauthorized (token expired) - but NOT for login requests
    if (error.response?.status === 401 && !originalRequest._retry && !isLoginRequest) {
      originalRequest._retry = true;

      // Try to refresh token (if refresh endpoint exists)
      // For now, just logout the user
      localStorage.removeItem('access_token');
      toast.error('Session expired. Please login again.');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle other errors
    if (error.response?.status === 402) {
      toast.error('Insufficient tokens. Please upgrade your plan.');
    } else if (error.response?.status === 403) {
      toast.error('Access denied. You don\'t have permission for this action.');
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    }

    return Promise.reject(error);
  }
);

export default api;
