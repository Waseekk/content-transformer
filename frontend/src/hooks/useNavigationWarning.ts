/**
 * Navigation Warning Hook
 * Warns user when trying to navigate away while operations are pending
 */

import { useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';

/**
 * Hook to warn user when navigating away with pending operations
 * Uses browser's beforeunload event for tab close/refresh
 */
export const useNavigationWarning = () => {
  const { pendingOperations } = useAppStore();

  const hasPendingOps = Object.values(pendingOperations).some(
    (op) => op.status === 'pending'
  );

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasPendingOps) {
        e.preventDefault();
        e.returnValue = 'You have operations in progress. Are you sure you want to leave?';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasPendingOps]);

  return { hasPendingOps };
};
