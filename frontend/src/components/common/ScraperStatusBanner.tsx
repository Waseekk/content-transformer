/**
 * ScraperStatusBanner - Real-time scraper status using Server-Sent Events
 */

import React, { useEffect, useState, useCallback } from 'react';
import { HiRefresh, HiCheck, HiX, HiInformationCircle } from 'react-icons/hi';
import { useQueryClient } from '@tanstack/react-query';

interface ScraperStatus {
  job_id: number;
  status: string;
  progress: number;
  status_message: string;
  current_site: string;
  articles_count: number | null;
  articles_saved: number | null;
  sites_completed: number;
  total_sites: number;
  site_stats: Record<string, number>;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
}

interface ScraperStatusBannerProps {
  jobId: number | null;
  onComplete?: (articlesCount: number) => void;
  onClose?: () => void;
}

export const ScraperStatusBanner: React.FC<ScraperStatusBannerProps> = ({
  jobId,
  onComplete,
  onClose,
}) => {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<ScraperStatus | null>(null);
  const [, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const connectSSE = useCallback(() => {
    if (!jobId) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Not authenticated');
      return;
    }

    // Create EventSource with auth token in URL (SSE doesn't support headers)
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const url = `${baseUrl}/api/scraper/status/${jobId}/stream?token=${token}`;

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setIsConnected(true);
      setIsVisible(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ScraperStatus;

        if (data.error) {
          setError(data.error);
          eventSource.close();
          return;
        }

        setStatus(data);

        // Check if job completed
        if (data.status === 'completed') {
          eventSource.close();
          setIsConnected(false);
          // Invalidate sessions cache so History tab shows new session
          queryClient.invalidateQueries({ queryKey: ['scrapingSessions'] });
          queryClient.invalidateQueries({ queryKey: ['articleStats'] });
          if (onComplete) {
            onComplete(data.articles_count || data.articles_saved || 0);
          }
        } else if (data.status === 'failed') {
          eventSource.close();
          setIsConnected(false);
          setError(data.error || 'Scraping failed');
        }
      } catch (e) {
        console.error('Failed to parse SSE data:', e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      // Don't show error if we intentionally closed (job completed)
      if (status?.status !== 'completed' && status?.status !== 'failed') {
        setError('Connection lost. Retrying...');
        // EventSource auto-reconnects, but let's close and retry manually after delay
        eventSource.close();
        setTimeout(() => connectSSE(), 2000);
      }
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, onComplete, status?.status, queryClient]);

  useEffect(() => {
    if (jobId) {
      const cleanup = connectSSE();
      return cleanup;
    }
  }, [jobId, connectSSE]);

  const handleClose = () => {
    setIsVisible(false);
    if (onClose) {
      onClose();
    }
  };

  // Don't render if no job or not visible
  if (!jobId || !isVisible) return null;

  // Determine banner color based on status
  const getBannerStyle = () => {
    if (error || status?.status === 'failed') {
      return 'bg-red-500';
    }
    if (status?.status === 'completed') {
      return 'bg-green-500';
    }
    return 'bg-gradient-to-r from-teal-500 to-cyan-500';
  };

  const getIcon = () => {
    if (error || status?.status === 'failed') {
      return <HiX className="w-5 h-5" />;
    }
    if (status?.status === 'completed') {
      return <HiCheck className="w-5 h-5" />;
    }
    return <HiRefresh className="w-5 h-5 animate-spin" />;
  };

  return (
    <div className={`fixed top-0 left-0 right-0 z-50 ${getBannerStyle()} text-white shadow-lg`}>
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Icon and Status */}
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-white/20 rounded-full">
              {getIcon()}
            </div>
            <div>
              <div className="font-semibold">
                {status?.status === 'completed'
                  ? 'Scraping Complete!'
                  : status?.status === 'failed'
                  ? 'Scraping Failed'
                  : 'Scraping in Progress...'}
              </div>
              <div className="text-sm text-white/90">
                {error || status?.status_message || 'Initializing...'}
              </div>
            </div>
          </div>

          {/* Center: Progress */}
          {status && status.status !== 'completed' && status.status !== 'failed' && (
            <div className="hidden md:flex items-center gap-4">
              {/* Progress Bar */}
              <div className="w-48">
                <div className="flex justify-between text-xs mb-1">
                  <span>Progress</span>
                  <span>{status.progress}%</span>
                </div>
                <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white rounded-full transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  />
                </div>
              </div>

              {/* Sites Progress */}
              {status.total_sites > 0 && (
                <div className="text-sm">
                  <span className="font-semibold">{status.sites_completed}</span>
                  <span className="text-white/80">/{status.total_sites} sites</span>
                </div>
              )}

              {/* Articles Found */}
              {(status.articles_count || status.articles_saved) && (
                <div className="flex items-center gap-1 text-sm">
                  <HiInformationCircle className="w-4 h-4" />
                  <span className="font-semibold">
                    {status.articles_count || status.articles_saved}
                  </span>
                  <span className="text-white/80">articles</span>
                </div>
              )}
            </div>
          )}

          {/* Right: Articles count (when complete) and Close button */}
          <div className="flex items-center gap-3">
            {status?.status === 'completed' && (
              <div className="text-sm bg-white/20 px-3 py-1 rounded-full">
                {status.articles_saved || status.articles_count || 0} articles saved
              </div>
            )}
            <button
              onClick={handleClose}
              className="p-1.5 hover:bg-white/20 rounded-full transition-colors"
              title="Close"
            >
              <HiX className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Mobile: Progress bar below */}
        {status && status.status !== 'completed' && status.status !== 'failed' && (
          <div className="md:hidden mt-2">
            <div className="flex justify-between text-xs mb-1">
              <span>{status.progress}% complete</span>
              {status.total_sites > 0 && (
                <span>{status.sites_completed}/{status.total_sites} sites</span>
              )}
            </div>
            <div className="h-1.5 bg-white/30 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-300"
                style={{ width: `${status.progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
