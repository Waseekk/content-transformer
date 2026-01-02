/**
 * Articles Hooks - React Query hooks for articles API
 */

import { useQuery } from '@tanstack/react-query';
import { articlesApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';

export const useArticles = () => {
  const filters = useAppStore((state) => state.filters);

  return useQuery({
    queryKey: ['articles', filters],
    queryFn: () => articlesApi.getAll({
      search: filters.search || undefined,
      sources: filters.sources.length > 0 ? filters.sources : undefined,
      page: filters.page,
      limit: filters.pageSize,
    }),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

export const useArticleStats = () => {
  return useQuery({
    queryKey: ['articleStats'],
    queryFn: articlesApi.getStats,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useArticleSources = () => {
  return useQuery({
    queryKey: ['articleSources'],
    queryFn: articlesApi.getSources,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};
