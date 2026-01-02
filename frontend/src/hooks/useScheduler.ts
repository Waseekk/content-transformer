/**
 * Scheduler Hooks - React Query hooks for scheduler API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { schedulerApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

export const useStartScheduler = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (intervalHours: number) => schedulerApi.start(intervalHours),
    onSuccess: (data) => {
      toast.success(`Scheduler started! Interval: ${data.interval_hours}h`);
      useAppStore.getState().setSchedulerStatus(data);
      queryClient.invalidateQueries({ queryKey: ['schedulerStatus'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start scheduler');
    },
  });
};

export const useStopScheduler = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: schedulerApi.stop,
    onSuccess: () => {
      toast.success('Scheduler stopped');
      useAppStore.getState().setSchedulerStatus(null);
      queryClient.invalidateQueries({ queryKey: ['schedulerStatus'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to stop scheduler');
    },
  });
};

export const useSchedulerStatus = () => {
  return useQuery({
    queryKey: ['schedulerStatus'],
    queryFn: schedulerApi.getStatus,
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 25000,
  });
};

export const useSchedulerHistory = (limit: number = 10) => {
  return useQuery({
    queryKey: ['schedulerHistory', limit],
    queryFn: () => schedulerApi.getHistory(limit),
    staleTime: 1000 * 60, // 1 minute
  });
};
