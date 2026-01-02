import { useState, useEffect } from 'react';
import { startScraper, getScraperStatus, getScraperResult, type ScraperJob } from '../../api/scraper';
import { Card, Button, Badge } from '../common';
import toast from 'react-hot-toast';

export function ScraperControls() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentJob, setCurrentJob] = useState<ScraperJob | null>(null);
  const [result, setResult] = useState<any>(null);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);

  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleStartScraper = async () => {
    try {
      setIsRunning(true);
      setResult(null);

      const job = await startScraper();
      setCurrentJob(job);
      toast.success('Scraper started!');

      // Start polling for status
      const interval = setInterval(async () => {
        try {
          const status = await getScraperStatus(job.job_id);
          setCurrentJob(status);

          if (status.status === 'completed') {
            clearInterval(interval);
            setIsRunning(false);

            // Get final result
            const finalResult = await getScraperResult(job.job_id);
            setResult(finalResult);
            toast.success(`Scraper completed! ${finalResult.total_articles} articles found.`);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setIsRunning(false);
            toast.error(`Scraper failed: ${status.error || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 3000); // Poll every 3 seconds

      setPollingInterval(interval);
    } catch (error: any) {
      setIsRunning(false);
      const errorMsg = error.response?.data?.detail || 'Failed to start scraper';
      toast.error(errorMsg);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
      pending: 'default',
      running: 'info',
      completed: 'success',
      failed: 'danger',
    };
    return <Badge variant={variants[status] || 'default'}>{status.toUpperCase()}</Badge>;
  };

  return (
    <div className="space-y-6">
      <Card title="Scraper Controls" subtitle="Collect latest travel news articles from configured sources">
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <Button
              variant="primary"
              onClick={handleStartScraper}
              disabled={isRunning}
              isLoading={isRunning}
            >
              {isRunning ? 'Scraping...' : 'Start Scraper'}
            </Button>

            {currentJob && (
              <div className="flex items-center gap-2">
                {getStatusBadge(currentJob.status)}
                {currentJob.progress !== undefined && (
                  <span className="text-sm text-gray-600">
                    {Math.round(currentJob.progress)}% complete
                  </span>
                )}
              </div>
            )}
          </div>

          {currentJob && currentJob.status === 'running' && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Current Progress</span>
                  <span className="text-sm text-gray-600">
                    {currentJob.progress !== undefined ? `${Math.round(currentJob.progress)}%` : '...'}
                  </span>
                </div>

                {currentJob.progress !== undefined && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${currentJob.progress}%` }}
                    />
                  </div>
                )}

                {currentJob.current_site && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Scraping:</span> {currentJob.current_site}
                  </div>
                )}

                <div className="grid grid-cols-3 gap-4 text-sm">
                  {currentJob.articles_scraped !== undefined && (
                    <div>
                      <span className="text-gray-500">Articles:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {currentJob.articles_scraped}
                      </span>
                    </div>
                  )}
                  {currentJob.sites_completed !== undefined && currentJob.total_sites !== undefined && (
                    <div>
                      <span className="text-gray-500">Sites:</span>
                      <span className="ml-2 font-semibold text-gray-900">
                        {currentJob.sites_completed}/{currentJob.total_sites}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {currentJob && currentJob.status === 'failed' && currentJob.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">
                <span className="font-semibold">Error:</span> {currentJob.error}
              </p>
            </div>
          )}
        </div>
      </Card>

      {result && (
        <Card
          title="Scraper Results"
          className="bg-gradient-to-br from-green-50 to-white border border-green-200"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <div className="text-3xl font-bold text-green-600">
                {result.total_articles}
              </div>
              <div className="text-sm text-gray-600 mt-1">Total Articles</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="text-3xl font-bold text-blue-600">
                {result.new_articles}
              </div>
              <div className="text-sm text-gray-600 mt-1">New Articles</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-purple-200">
              <div className="text-3xl font-bold text-purple-600">
                {result.sites_scraped}
              </div>
              <div className="text-sm text-gray-600 mt-1">Sites Scraped</div>
            </div>
          </div>

          {result.articles && result.articles.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Recent Articles</h3>
              <div className="space-y-2">
                {result.articles.slice(0, 5).map((article: any, index: number) => (
                  <div
                    key={index}
                    className="p-3 bg-white rounded border border-gray-200 hover:shadow-sm transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 text-sm">{article.title}</p>
                        <p className="text-xs text-gray-500 mt-1">{article.source}</p>
                      </div>
                      <Badge variant="success" size="sm">
                        New
                      </Badge>
                    </div>
                  </div>
                ))}
                {result.articles.length > 5 && (
                  <p className="text-sm text-gray-500 text-center mt-3">
                    ... and {result.articles.length - 5} more articles
                  </p>
                )}
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
