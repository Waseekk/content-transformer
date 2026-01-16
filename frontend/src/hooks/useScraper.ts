/**
 * Scraper Hooks - React Query hooks for scraper API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useUpdateEnabledSites = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: scraperApi.updateEnabledSites,
    onSuccess: (data) => {
      // Update the cache with new data
      queryClient.setQueryData(['scraperSites'], (old: any) => ({
        ...old,
        enabled_sites: data.enabled_sites,
        default_sites: data.default_sites,
        use_custom_default: data.use_custom_default,
        available_sites: old?.available_sites?.map((site: any) => ({
          ...site,
          enabled: data.enabled_sites.includes(site.name),
        })),
      }));
      // Invalidate all article-related queries since they depend on enabled sites
      queryClient.invalidateQueries({ queryKey: ['articleStats'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      queryClient.invalidateQueries({ queryKey: ['articleSources'] }); // Sources dropdown
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update sites');
    },
  });
};

export const useSetDefaultSites = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: scraperApi.setDefaultSites,
    onSuccess: (data) => {
      queryClient.setQueryData(['scraperSites'], (old: any) => ({
        ...old,
        default_sites: data.default_sites,
        use_custom_default: data.use_custom_default,
      }));
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to set default sites');
    },
  });
};

export const useClearDefaultSites = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: scraperApi.clearDefaultSites,
    onSuccess: (data) => {
      queryClient.setQueryData(['scraperSites'], (old: any) => ({
        ...old,
        enabled_sites: data.enabled_sites,
        default_sites: data.default_sites,
        use_custom_default: data.use_custom_default,
        available_sites: old?.available_sites?.map((site: any) => ({
          ...site,
          enabled: data.enabled_sites.includes(site.name),
        })),
      }));
      // Invalidate all article-related queries since enabled sites changed
      queryClient.invalidateQueries({ queryKey: ['articleStats'] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      queryClient.invalidateQueries({ queryKey: ['articleSources'] }); // Sources dropdown
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to clear default');
    },
  });
};
