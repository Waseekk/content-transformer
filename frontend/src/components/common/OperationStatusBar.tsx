/**
 * Operation Status Bar - Global floating bar showing pending operations
 * Appears on all pages when operations are in progress
 * Note: Error notifications are hidden from users - only pending/completed shown
 */

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { HiSparkles, HiCheckCircle, HiX, HiArrowRight } from 'react-icons/hi';
import { useAppStore } from '../../store/useAppStore';
import type { PendingOperation } from '../../store/useAppStore';

export const OperationStatusBar: React.FC = () => {
  const { pendingOperations, clearOperation } = useAppStore();

  // Get all operations
  const operations = Object.values(pendingOperations);

  // Separate by status
  const pending = operations.filter(op => op.status === 'pending');
  const completed = operations.filter(op => op.status === 'completed');
  const errors = operations.filter(op => op.status === 'error');

  // Auto-clear error operations silently (don't show to users)
  useEffect(() => {
    if (errors.length > 0) {
      errors.forEach(op => clearOperation(op.id));
    }
  }, [errors, clearOperation]);

  const getOperationLabel = (type: PendingOperation['type']) => {
    switch (type) {
      case 'translation': return 'Processing content';
      case 'enhancement': return 'Generating news articles';
      case 'url_extraction': return 'Extracting from URL';
      default: return 'Processing';
    }
  };

  // Show nothing if no pending or completed operations
  if (pending.length === 0 && completed.length === 0) return null;

  return (
    <AnimatePresence>
      {/* Pending Operations */}
      {pending.length > 0 && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50"
        >
          <div className="bg-gradient-to-r from-ai-primary to-ai-secondary text-white px-6 py-3 rounded-2xl shadow-glow-md flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            >
              <HiSparkles className="w-5 h-5" />
            </motion.div>
            <p className="font-medium">
              {pending.map(op => getOperationLabel(op.type)).join(', ')}...
            </p>
            <Link
              to="/translation"
              className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors flex items-center gap-1"
            >
              View <HiArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </motion.div>
      )}

      {/* Completed Operations */}
      {pending.length === 0 && completed.length > 0 && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50"
        >
          <div className="bg-emerald-500 text-white px-6 py-3 rounded-2xl shadow-lg flex items-center gap-4">
            <HiCheckCircle className="w-5 h-5" />
            <div>
              <p className="font-medium">
                {completed.length} operation{completed.length > 1 ? 's' : ''} completed!
              </p>
              <p className="text-sm text-white/80">
                Results are ready
              </p>
            </div>
            <Link
              to="/translation"
              className="ml-2 px-3 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors flex items-center gap-1"
            >
              View Results <HiArrowRight className="w-4 h-4" />
            </Link>
            <button
              onClick={() => completed.forEach(op => clearOperation(op.id))}
              className="p-1 hover:bg-white/20 rounded-lg transition-colors"
            >
              <HiX className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Error operations are auto-cleared silently - not shown to users */}
    </AnimatePresence>
  );
};
