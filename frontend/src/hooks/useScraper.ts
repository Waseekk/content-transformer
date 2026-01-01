/**
 * Scraper Hooks - React Query hooks for scraper API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { scraperApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

export const useStartScraper = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: scraperApi.start,
    onSuccess: (data) => {
      toast.success('Scraper started!');
      // Start polling for status
      useAppStore.getState().setScraperStatus({
        is_running: true,
        progress: 0,
        current_site: null,
        articles_count: 0,
        status_message: 'Starting...',
        site_stats: {},
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start scraper');
    },
  });
};

export const useScraperStatus = (jobId: string | null, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['scraperStatus', jobId],
    queryFn: () => scraperApi.getStatus(jobId!),
    enabled: enabled && !!jobId,
    refetchInterval: enabled ? 3000 : false, // Poll every 3 seconds when enabled
  });
};

export const useScraperSites = () => {
  return useQuery({
    queryKey: ['scraperSites'],
    queryFn: scraperApi.getSites,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};
