/**
 * Scraper Hooks - React Query hooks for scraper API
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { scraperApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

export const useStartScraper = () => {
  return useMutation({
    mutationFn: scraperApi.start,
    onSuccess: (data) => {
      // Set the active job ID to trigger SSE connection
      useAppStore.getState().setActiveScraperJobId(data.job_id);
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
