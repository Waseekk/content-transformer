/**
 * Google News Search Hooks - React Query hooks for Google News search API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { searchApi } from '../services/api';
import type { GoogleNewsSearchResponse } from '../services/api';
import toast from 'react-hot-toast';

/**
 * Hook for performing Google News searches
 */
export const useGoogleNewsSearch = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: searchApi.searchGoogleNews,
    onSuccess: (data: GoogleNewsSearchResponse) => {
      if (data.success) {
        // Invalidate paginated results to force refetch
        queryClient.invalidateQueries({ queryKey: ['googleNewsPaginated'] });

        if (data.cached) {
          toast.success(`Found ${data.total_results} results (cached)`);
        } else {
          toast.success(`Found ${data.total_results} results in ${data.search_time_ms}ms`);
        }
      } else {
        toast.error(data.error_message || 'Search failed');
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Search failed. Please try again.';
      toast.error(message);
    },
  });
};

/**
 * Hook for getting paginated search results
 * Must call useGoogleNewsSearch first to populate cache
 */
export const usePaginatedGoogleNewsSearch = (
  keyword: string,
  timeFilter: string,
  page: number,
  limit: number,
  enabled: boolean = false
) => {
  return useQuery({
    queryKey: ['googleNewsPaginated', keyword, timeFilter, page, limit],
    queryFn: () => searchApi.getPaginatedResults({
      keyword,
      time_filter: timeFilter,
      page,
      limit,
    }),
    enabled: enabled && !!keyword,
    staleTime: 1000 * 60 * 5, // 5 minutes (matches backend cache)
  });
};

/**
 * Hook for clearing search cache
 */
export const useClearSearchCache = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: searchApi.clearSearchCache,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['googleNewsPaginated'] });
      toast.success('Search cache cleared');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to clear cache');
    },
  });
};
