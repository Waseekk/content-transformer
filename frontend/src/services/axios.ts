/**
 * Axios Configuration
 * Configured axios instance with base URL and JWT interceptors
 */

import axios from 'axios';

// In production, use empty string (paths already include /api)
// In development, use /api as fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes timeout for long operations like extraction/enhancement
  // Serialize arrays as repeated params (sources=a&sources=b) for FastAPI
  paramsSerializer: {
    indexes: null, // This removes the brackets from array params
  },
});

// Request interceptor - Add JWT token to requests
axiosInstance.interceptors.request.use(
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

// Response interceptor - Handle 401 errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
