/**
 * Translation Hooks - React Query hooks for translation API
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { translationApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

export const useTranslate = () => {
  return useMutation({
    mutationFn: ({ text, inputLanguage = 'auto' }: { text: string; inputLanguage?: 'auto' | 'en' | 'bn' }) => {
      const selectedArticle = useAppStore.getState().selectedArticle;
      const title = selectedArticle?.headline || 'Untitled Article';
      return translationApi.translateText(text, title, inputLanguage);
    },
    onSuccess: (data) => {
      toast.success('Translation complete!');
      useAppStore.getState().setCurrentTranslation({
        original: data.original_text || '',
        translated: data.translated_text,
        tokens_used: data.tokens_used,
        article: useAppStore.getState().selectedArticle || undefined,
        timestamp: new Date().toISOString(),
      });
    },
    onError: (error: any) => {
      // Handle validation errors (array of error objects)
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        const errorMsg = detail.map((err: any) => err.msg || err.message).join(', ');
        toast.error(errorMsg || 'Validation error');
      } else if (typeof detail === 'string') {
        toast.error(detail);
      } else {
        toast.error('Translation failed');
      }
    },
  });
};

export const useTranslationHistory = (limit: number = 50) => {
  return useQuery({
    queryKey: ['translationHistory', limit],
    queryFn: () => translationApi.getHistory(limit),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};
