/**
 * Articles Hooks - React Query hooks for articles API
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { articlesApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

// Get all unique articles by default (no job filter)
export const useArticles = (options?: { latestOnly?: boolean; jobId?: number }) => {
  const filters = useAppStore((state) => state.filters);
  const latestOnly = options?.latestOnly ?? false; // Default to false - show all unique articles
  const jobId = options?.jobId;

  return useQuery({
    queryKey: ['articles', filters, latestOnly, jobId],
    queryFn: () => articlesApi.getAll({
      search: filters.search || undefined,
      sources: filters.sources.length > 0 ? filters.sources : undefined,
      page: filters.page,
      limit: filters.pageSize,
      latest_only: latestOnly,
      job_id: jobId,
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

// Get scraping session history (past sessions excluding latest)
export const useScrapingSessions = (
  params?: { days?: number; page?: number; limit?: number },
  options?: { refetchInterval?: number | false }
) => {
  return useQuery({
    queryKey: ['scrapingSessions', params],
    queryFn: () => articlesApi.getScrapingSessions(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: options?.refetchInterval,
  });
};

// Delete a single scraping session
export const useDeleteSession = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: articlesApi.deleteSession,
    onSuccess: (data) => {
      // Invalidate all related queries
      queryClient.invalidateQueries({ queryKey: ['scrapingSessions'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      queryClient.invalidateQueries({ queryKey: ['articleStats'] });
      queryClient.invalidateQueries({ queryKey: ['articleSources'] });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete session');
    },
  });
};

// Delete all scraping history (full reset)
export const useDeleteAllHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: articlesApi.deleteAllHistory,
    onSuccess: (data) => {
      // Invalidate all related queries
      queryClient.invalidateQueries({ queryKey: ['scrapingSessions'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      queryClient.invalidateQueries({ queryKey: ['articleStats'] });
      queryClient.invalidateQueries({ queryKey: ['articleSources'] });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete history');
    },
  });
};
