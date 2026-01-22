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

  deleteSession: async (jobId: number) => {
    const response = await axios.delete(`/api/articles/history/sessions/${jobId}`);
    return response.data;
  },

  deleteAllHistory: async () => {
    const response = await axios.delete('/api/articles/history/sessions');
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

  updateEnabledSites: async (enabledSites: string[]) => {
    const response = await axios.put('/api/scraper/sites', {
      enabled_sites: enabledSites,
    });
    return response.data;
  },

  setDefaultSites: async () => {
    const response = await axios.post('/api/scraper/sites/default');
    return response.data;
  },

  clearDefaultSites: async () => {
    const response = await axios.delete('/api/scraper/sites/default');
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

  translateText: async (text: string, title?: string, inputLanguage: 'auto' | 'en' | 'bn' = 'auto') => {
    const response = await axios.post('/api/translate/translate-text', {
      text,
      title: title || 'Untitled',
      save_to_history: true,
      input_language: inputLanguage,
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

  getSessions: async (days: number = 7) => {
    const response = await axios.get('/api/articles/enhancement-sessions', {
      params: { days },
    });
    return response.data;
  },

  getById: async (enhancementId: number) => {
    const response = await axios.get(`/api/enhance/${enhancementId}`);
    return response.data;
  },
};

// ============================================================================
// EXTRACTION
// ============================================================================

export interface URLExtractionResponse {
  success: boolean;
  content: string | null;
  title: string | null;
  extraction_method: string | null;
  error_message: string | null;
}

export interface URLExtractAndTranslateResponse {
  success: boolean;
  english_content: string | null;
  bengali_content: string | null;
  title: string | null;
  extraction_method: string | null;
  tokens_used: number;
  tokens_remaining: number;
  error_message: string | null;
}

export const extractionApi = {
  // Extract only (no translation)
  extractFromURL: async (url: string): Promise<URLExtractionResponse> => {
    const response = await axios.post<URLExtractionResponse>('/api/extract/url', {
      url,
    });
    return response.data;
  },

  // Extract AND translate in one step
  extractAndTranslate: async (url: string): Promise<URLExtractAndTranslateResponse> => {
    const response = await axios.post<URLExtractAndTranslateResponse>('/api/extract/url-and-translate', {
      url,
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

// ============================================================================
// GOOGLE NEWS SEARCH
// ============================================================================

export interface GoogleNewsResult {
  title: string;
  url: string;
  source: string | null;
  published_time: string | null;
  snippet: string | null;
}

export interface GoogleNewsSearchResponse {
  success: boolean;
  keyword: string;
  total_results: number;
  results: GoogleNewsResult[];
  search_time_ms: number;
  cached: boolean;
  error_message: string | null;
}

export interface PaginatedSearchResponse {
  success: boolean;
  results: GoogleNewsResult[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  keyword: string;
  time_filter: string;
  cached: boolean;
  error_message: string | null;
}

export const searchApi = {
  searchGoogleNews: async (params: {
    keyword: string;
    time_filter?: string;
    max_results?: number;
  }): Promise<GoogleNewsSearchResponse> => {
    const response = await axios.post<GoogleNewsSearchResponse>('/api/search/google-news', {
      keyword: params.keyword,
      time_filter: params.time_filter || '24h',
      max_results: params.max_results || 50,
    });
    return response.data;
  },

  getPaginatedResults: async (params: {
    keyword: string;
    time_filter?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedSearchResponse> => {
    const response = await axios.get<PaginatedSearchResponse>('/api/search/google-news/paginated', {
      params: {
        keyword: params.keyword,
        time_filter: params.time_filter || '24h',
        page: params.page || 1,
        limit: params.limit || 10,
      },
    });
    return response.data;
  },

  clearSearchCache: async () => {
    const response = await axios.delete('/api/search/google-news/cache');
    return response.data;
  },
};
