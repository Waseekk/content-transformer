/**
 * Enhancement History Hook - React Query hook for enhancement sessions API
 */

import { useQuery } from '@tanstack/react-query';
import { enhancementApi } from '../services/api';

// Types for enhancement session data
export interface EnhancementData {
  id: number;
  content: string;
  word_count: number;
  tokens_used: number;
  created_at: string;
}

export interface EnhancementSession {
  translation_id: number | null;
  headline: string;
  english_content: string | null;
  hard_news: EnhancementData | null;
  soft_news: EnhancementData | null;
  created_at: string;
}

export interface EnhancementSessionGroup {
  date: string;
  sessions: EnhancementSession[];
  count: number;
}

export interface EnhancementSessionsResponse {
  enhancement_sessions: EnhancementSessionGroup[];
  total_sessions: number;
  date_range_days: number;
}

/**
 * Hook to fetch enhancement sessions grouped by date
 */
export const useEnhancementSessions = (days: number = 7) => {
  return useQuery<EnhancementSessionsResponse>({
    queryKey: ['enhancementSessions', days],
    queryFn: () => enhancementApi.getSessions(days),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

/**
 * Hook to fetch a single enhancement by ID
 */
export const useEnhancement = (enhancementId: number | null) => {
  return useQuery({
    queryKey: ['enhancement', enhancementId],
    queryFn: () => enhancementApi.getById(enhancementId!),
    enabled: !!enhancementId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
