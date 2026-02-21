/**
 * URL Extraction Hooks - React Query hooks for URL content extraction API
 */

import { useMutation } from '@tanstack/react-query';
import { extractionApi } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

/**
 * Hook for extracting content from URL only (no translation)
 */
export const useURLExtraction = () => {
  return useMutation({
    mutationFn: (url: string) => extractionApi.extractFromURL(url),
    onSuccess: (data) => {
      if (data.success) {
        // silent success
      } else {
        toast.error(
          data.error_message || 'Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction.',
          { duration: 5000 }
        );
      }
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'string'
        ? detail
        : 'Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction.';

      toast.error(message, { duration: 5000 });
    },
  });
};

/**
 * Hook for extracting AND translating from URL in one step
 * Uses global operation tracking so results persist across navigation
 */
export const useURLExtractAndTranslate = () => {
  const { startOperation, completeOperation, failOperation } = useAppStore();

  return useMutation({
    mutationFn: async (url: string) => {
      const operationId = `url_extract_${Date.now()}`;
      startOperation(operationId, 'url_extraction');

      try {
        const result = await extractionApi.extractAndTranslate(url);

        if (result.success) {
          completeOperation(operationId, result);
        } else {
          failOperation(operationId, result.error_message || 'Extraction failed');
        }

        return { ...result, operationId };
      } catch (error) {
        failOperation(operationId, 'Network error');
        throw error;
      }
    },
    onSuccess: (data) => {
      if (data.success) {
        // silent success
      } else {
        toast.error(
          data.error_message || 'Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction.',
          { duration: 5000 }
        );
      }
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'string'
        ? detail
        : 'Failed to extract content, please contact admin if the problem persists.\n\nNB: Some websites may need manual extraction.';

      toast.error(message, { duration: 5000 });
    },
  });
};
