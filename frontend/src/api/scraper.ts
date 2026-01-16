import axios from './axios';

export interface ScraperSite {
  id?: number;
  name: string;
  url: string;
  enabled: boolean;
  description?: string;
}

export interface UserSitesResponse {
  enabled_sites: string[];
  available_sites: ScraperSite[];
  default_sites: string[];
  use_custom_default: boolean;
}

export interface SitesUpdateResponse {
  success: boolean;
  enabled_sites: string[];
  default_sites: string[];
  use_custom_default: boolean;
  message: string;
}

export interface ScraperJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  current_site?: string;
  articles_scraped?: number;
  sites_completed?: number;
  total_sites?: number;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface ScraperResult {
  total_articles: number;
  sites_scraped: number;
  new_articles: number;
  articles: any[];
}

// Start scraper job
export const startScraper = async (
  sites?: string[],
  views?: string[]
): Promise<ScraperJob> => {
  const response = await axios.post('/api/scraper/run', {
    sites,
    views,
  });
  return response.data;
};

// Get scraper job status
export const getScraperStatus = async (jobId: string): Promise<ScraperJob> => {
  const response = await axios.get(`/api/scraper/status/${jobId}`);
  return response.data;
};

// Get scraper job result
export const getScraperResult = async (jobId: string): Promise<ScraperResult> => {
  const response = await axios.get(`/api/scraper/result/${jobId}`);
  return response.data;
};

// Get available sites with user's enabled status
export const getScraperSites = async (): Promise<UserSitesResponse> => {
  const response = await axios.get('/api/scraper/sites');
  return response.data;
};

// Update user's enabled sites (instant save on toggle)
export const updateEnabledSites = async (enabledSites: string[]): Promise<SitesUpdateResponse> => {
  const response = await axios.put('/api/scraper/sites', {
    enabled_sites: enabledSites,
  });
  return response.data;
};

// Set current enabled sites as user's default
export const setDefaultSites = async (): Promise<SitesUpdateResponse> => {
  const response = await axios.post('/api/scraper/sites/default');
  return response.data;
};

// Clear custom default and use system default
export const clearDefaultSites = async (): Promise<SitesUpdateResponse> => {
  const response = await axios.delete('/api/scraper/sites/default');
  return response.data;
};

// Get scraper job history
export const getScraperJobs = async (
  page: number = 1,
  size: number = 10
): Promise<{
  items: ScraperJob[];
  total: number;
  page: number;
  size: number;
  pages: number;
}> => {
  const response = await axios.get('/api/scraper/jobs', {
    params: { skip: (page - 1) * size, limit: size },
  });
  return response.data;
};
