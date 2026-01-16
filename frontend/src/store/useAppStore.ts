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
  pastedContent: string;
  currentTranslation: TranslationResult | null;
  translationHistory: TranslationResult[];

  // Enhancement
  selectedFormats: string[];
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

  setPastedContent: (content: string) => void;
  setCurrentTranslation: (translation: TranslationResult | null) => void;
  addToTranslationHistory: (translation: TranslationResult) => void;
  clearTranslationState: () => void;

  setSelectedFormats: (formats: string[]) => void;
  toggleFormat: (formatId: string) => void;
  setCurrentEnhancements: (enhancements: Record<string, EnhancementResult>) => void;
  addEnhancement: (formatType: string, enhancement: EnhancementResult) => void;
  clearEnhancementState: () => void;

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
      pastedContent: '',
      currentTranslation: null,
      translationHistory: [],
      selectedFormats: [],
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

      setPastedContent: (content) => set({ pastedContent: content }),

      setCurrentTranslation: (translation) => set({ currentTranslation: translation }),

      addToTranslationHistory: (translation) => set((state) => ({
        translationHistory: [translation, ...state.translationHistory].slice(0, 50) // Keep last 50
      })),

      clearTranslationState: () => set({
        pastedContent: '',
        currentTranslation: null,
        selectedFormats: [],
        currentEnhancements: {},
      }),

      setSelectedFormats: (formats) => set({ selectedFormats: formats }),

      toggleFormat: (formatId) => set((state) => ({
        selectedFormats: state.selectedFormats.includes(formatId)
          ? state.selectedFormats.filter((id) => id !== formatId)
          : [...state.selectedFormats, formatId]
      })),

      setCurrentEnhancements: (enhancements) => set({ currentEnhancements: enhancements }),

      addEnhancement: (formatType, enhancement) => set((state) => ({
        currentEnhancements: {
          ...state.currentEnhancements,
          [formatType]: enhancement
        }
      })),

      clearEnhancementState: () => set({
        selectedFormats: [],
        currentEnhancements: {},
      }),

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
        pastedContent: state.pastedContent,
        currentTranslation: state.currentTranslation,
        translationHistory: state.translationHistory,
        selectedFormats: state.selectedFormats,
        currentEnhancements: state.currentEnhancements,
      }),
    }
  )
);
