/**
 * Enhancement Hooks - React Query hooks for enhancement API
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { enhancementApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

export const useEnhance = () => {
  return useMutation({
    mutationFn: (data: {
      text: string;
      headline?: string;
      formats: string[];
      provider?: string;
      model?: string;
    }) => enhancementApi.enhance(data),
    onSuccess: (data) => {
      toast.success('Enhancement complete!');

      // Convert formats to store format
      const enhancements: Record<string, any> = {};
      data.formats.forEach((result: any) => {
        enhancements[result.format_type] = {
          format_type: result.format_type,
          content: result.content,
          tokens_used: result.tokens_used,
          timestamp: new Date().toISOString(),
        };
      });

      useAppStore.getState().setCurrentEnhancements(enhancements);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Enhancement failed');
    },
  });
};

export const useEnhancementFormats = () => {
  return useQuery({
    queryKey: ['enhancementFormats'],
    queryFn: enhancementApi.getFormats,
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

export const useEnhancementHistory = (limit: number = 50) => {
  return useQuery({
    queryKey: ['enhancementHistory', limit],
    queryFn: () => enhancementApi.getHistory(limit),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};
