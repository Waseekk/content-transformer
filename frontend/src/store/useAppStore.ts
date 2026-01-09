/**
 * Global App Store - Zustand
 * Manages application state with localStorage persistence
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Article,
  ArticleFilters,
  ScraperStatus,
  SchedulerStatus,
} from '../types';

export interface TranslationResult {
  original: string;
  translated: string;
  tokens_used: number;
  article?: Article;
  timestamp: string;
}

export interface EnhancementResult {
  format_type: 'hard_news' | 'soft_news';
  content: string;
  tokens_used: number;
  timestamp: string;
}

interface AppState {
  // Articles
  articles: Article[];
  selectedArticle: Article | null;
  filters: ArticleFilters;

  // Scraper
  scraperStatus: ScraperStatus | null;
  activeScraperJobId: number | null;

  // Scheduler
  schedulerStatus: SchedulerStatus | null;

  // Translation
  currentTranslation: TranslationResult | null;
  translationHistory: TranslationResult[];

  // Enhancement
  currentEnhancements: Record<string, EnhancementResult>;

  // UI State
  isPreviewPanelOpen: boolean;
  previewArticle: Article | null;

  // Actions
  setArticles: (articles: Article[]) => void;
  selectArticle: (article: Article | null) => void;
  setFilters: (filters: Partial<ArticleFilters>) => void;
  resetFilters: () => void;

  setScraperStatus: (status: ScraperStatus | null) => void;
  setActiveScraperJobId: (jobId: number | null) => void;
  setSchedulerStatus: (status: SchedulerStatus | null) => void;

  setCurrentTranslation: (translation: TranslationResult | null) => void;
  addToTranslationHistory: (translation: TranslationResult) => void;

  setCurrentEnhancements: (enhancements: Record<string, EnhancementResult>) => void;
  addEnhancement: (formatType: string, enhancement: EnhancementResult) => void;

  openPreviewPanel: (article: Article) => void;
  closePreviewPanel: () => void;
}

const defaultFilters: ArticleFilters = {
  search: '',
  sources: [],
  page: 1,
  pageSize: 10,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      articles: [],
      selectedArticle: null,
      filters: defaultFilters,
      scraperStatus: null,
      activeScraperJobId: null,
      schedulerStatus: null,
      currentTranslation: null,
      translationHistory: [],
      currentEnhancements: {},
      isPreviewPanelOpen: false,
      previewArticle: null,

      // Actions
      setArticles: (articles) => set({ articles }),

      selectArticle: (article) => set({
        selectedArticle: article,
        isPreviewPanelOpen: false,
        previewArticle: null,
      }),

      setFilters: (newFilters) => set((state) => ({
        filters: { ...state.filters, ...newFilters }
      })),

      resetFilters: () => set({ filters: defaultFilters }),

      setScraperStatus: (status) => set({ scraperStatus: status }),

      setActiveScraperJobId: (jobId) => set({ activeScraperJobId: jobId }),

      setSchedulerStatus: (status) => set({ schedulerStatus: status }),

      setCurrentTranslation: (translation) => set({ currentTranslation: translation }),

      addToTranslationHistory: (translation) => set((state) => ({
        translationHistory: [translation, ...state.translationHistory].slice(0, 50) // Keep last 50
      })),

      setCurrentEnhancements: (enhancements) => set({ currentEnhancements: enhancements }),

      addEnhancement: (formatType, enhancement) => set((state) => ({
        currentEnhancements: {
          ...state.currentEnhancements,
          [formatType]: enhancement
        }
      })),

      openPreviewPanel: (article) => set({
        isPreviewPanelOpen: true,
        previewArticle: article
      }),

      closePreviewPanel: () => set({
        isPreviewPanelOpen: false,
        previewArticle: null
      }),
    }),
    {
      name: 'travel-news-store', // localStorage key
      partialize: (state) => ({
        // Only persist these fields
        selectedArticle: state.selectedArticle,
        filters: state.filters,
        translationHistory: state.translationHistory,
      }),
    }
  )
);
