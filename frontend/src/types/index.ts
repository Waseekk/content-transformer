/**
 * Shared TypeScript Types
 */

export interface Article {
  id?: string;
  headline: string;
  publisher: string;
  country: string;
  published_time: string;
  article_url: string;
  scraped_at?: string;
  tags?: string[];
  content_preview?: string;
}

export interface ArticleFilters {
  search: string;
  sources: string[];
  page: number;
  pageSize: number;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface ScraperStatus {
  is_running: boolean;
  progress: number;
  current_site: string | null;
  articles_count: number;
  status_message: string;
  site_stats: Record<string, number>;
  start_time?: string;
  end_time?: string;
  error?: string;
}

export interface SchedulerStatus {
  is_running: boolean;
  interval_hours: number;
  next_run_time: string | null;
  time_until_next: string;
  run_count: number;
  last_run_time: string | null;
  last_run_articles: number | null;
}

export interface TranslationData {
  original: string;
  translated: string;
  tokens_used: number;
  article?: Article;
  timestamp: string;
}

export interface EnhancementFormat {
  format_type: string;
  content: string;
  tokens_used: number;
}
