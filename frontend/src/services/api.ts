/**
 * API Service - All backend endpoints
 */

import axios from './axios';

// ============================================================================
// ARTICLES
// ============================================================================

export const articlesApi = {
  getAll: async (params?: {
    search?: string;
    sources?: string[];
    page?: number;
    limit?: number;
    latest_only?: boolean;
    job_id?: number;
  }) => {
    const response = await axios.get('/api/articles/', { params });
    return response.data;
  },

  getStats: async () => {
    const response = await axios.get('/api/articles/stats');
    return response.data;
  },

  getSources: async () => {
    const response = await axios.get('/api/articles/sources/list');
    return response.data;
  },

  getScrapingSessions: async (params?: {
    days?: number;
    page?: number;
    limit?: number;
  }) => {
    const response = await axios.get('/api/articles/history/sessions', { params });
    return response.data;
  },
};

// ============================================================================
// SCRAPER
// ============================================================================

export const scraperApi = {
  start: async () => {
    const response = await axios.post('/api/scraper/run', {});
    return response.data;
  },

  getStatus: async (jobId: string) => {
    const response = await axios.get(`/api/scraper/status/${jobId}`);
    return response.data;
  },

  getResult: async (jobId: string) => {
    const response = await axios.get(`/api/scraper/result/${jobId}`);
    return response.data;
  },

  getSites: async () => {
    const response = await axios.get('/api/scraper/sites');
    return response.data;
  },
};

// ============================================================================
// SCHEDULER
// ============================================================================

export const schedulerApi = {
  start: async (intervalHours: number) => {
    const response = await axios.post('/api/scraper/scheduler/start', {
      interval_hours: intervalHours,
    });
    return response.data;
  },

  stop: async () => {
    const response = await axios.post('/api/scraper/scheduler/stop');
    return response.data;
  },

  getStatus: async () => {
    const response = await axios.get('/api/scraper/scheduler/status');
    return response.data;
  },

  getHistory: async (limit: number = 10) => {
    const response = await axios.get('/api/scraper/scheduler/history', {
      params: { limit },
    });
    return response.data;
  },
};

// ============================================================================
// TRANSLATION
// ============================================================================

export const translationApi = {
  extractAndTranslate: async (content: string) => {
    const response = await axios.post('/api/translate/extract-and-translate', {
      content,
    });
    return response.data;
  },

  translateText: async (text: string, title?: string) => {
    const response = await axios.post('/api/translate/translate-text', {
      text,
      title: title || 'Untitled',
      save_to_history: true,
    });
    return response.data;
  },

  getHistory: async (limit: number = 50) => {
    const response = await axios.get('/api/translate/', {
      params: { limit },
    });
    return response.data;
  },
};

// ============================================================================
// ENHANCEMENT
// ============================================================================

export const enhancementApi = {
  getFormats: async () => {
    const response = await axios.get('/api/enhance/formats');
    return response.data;
  },

  enhance: async (data: {
    text: string;
    headline?: string;
    formats: string[];
    provider?: string;
    model?: string;
  }) => {
    const response = await axios.post('/api/enhance/', data);
    return response.data;
  },

  getHistory: async (limit: number = 50) => {
    const response = await axios.get('/api/enhance/', {
      params: { limit },
    });
    return response.data;
  },
};

// ============================================================================
// AUTH
// ============================================================================

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await axios.post('/api/auth/login', {
      username: email,
      password,
    });
    return response.data;
  },

  register: async (data: {
    email: string;
    password: string;
    full_name: string;
  }) => {
    const response = await axios.post('/api/auth/register', data);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await axios.get('/api/auth/me');
    return response.data;
  },
};
