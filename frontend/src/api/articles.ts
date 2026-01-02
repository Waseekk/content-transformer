import axios from './axios';

export interface Article {
  id: number;
  title: string;
  url: string;
  source: string;
  published_date?: string;
  scraped_at: string;
  content?: string;
}

export interface ArticlesListResponse {
  items: Article[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ArticleStats {
  total_articles: number;
  total_sources: number;
  articles_today: number;
  articles_this_week: number;
  articles_this_month: number;
}

export interface SourceInfo {
  source: string;
  count: number;
}

// Get articles with pagination and filters
export const getArticles = async (
  page: number = 1,
  size: number = 10,
  source?: string,
  search?: string
): Promise<ArticlesListResponse> => {
  const params: any = {
    skip: (page - 1) * size,
    limit: size,
  };

  if (source) params.source = source;
  if (search) params.search = search;

  const response = await axios.get('/api/articles/', { params });
  return response.data;
};

// Get single article
export const getArticle = async (id: number): Promise<Article> => {
  const response = await axios.get(`/api/articles/${id}`);
  return response.data;
};

// Get article statistics
export const getArticleStats = async (): Promise<ArticleStats> => {
  const response = await axios.get('/api/articles/stats');
  return response.data;
};

// Get list of sources
export const getSources = async (): Promise<SourceInfo[]> => {
  const response = await axios.get('/api/articles/sources/list');
  return response.data.sources;
};

// Delete article
export const deleteArticle = async (id: number): Promise<void> => {
  await axios.delete(`/api/articles/${id}`);
};
