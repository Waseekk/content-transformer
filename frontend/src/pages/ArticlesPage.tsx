/**
 * Articles Page - Main article listing with filters and selection
 */

import { useState, useEffect, useCallback } from 'react';
import { useArticles, useArticleSources } from '../hooks/useArticles';
import { useStartScraper } from '../hooks/useScraper';
import { useAppStore } from '../store/useAppStore';
import { ArticleCard } from '../components/common/ArticleCard';
import { SearchableMultiSelect } from '../components/common/SearchableMultiSelect';
import { ScraperStatusBanner } from '../components/common/ScraperStatusBanner';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';

export const ArticlesPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const jobIdParam = searchParams.get('job_id');
  const jobId = jobIdParam ? parseInt(jobIdParam) : undefined;

  // If job_id is provided, show articles from that session (history mode)
  // Otherwise show articles from latest session (default)
  const { data: articlesData, isLoading, refetch } = useArticles({
    latestOnly: !jobId, // Only filter by latest if no job_id specified
    jobId: jobId,
  });
  const { data: sourcesData } = useArticleSources();
  const startScraper = useStartScraper();

  const {
    filters,
    setFilters,
    resetFilters,
    selectedArticle,
    selectArticle,
    activeScraperJobId,
    setActiveScraperJobId,
  } = useAppStore();

  const [searchInput, setSearchInput] = useState(filters.search);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters({ search: searchInput });
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const articles = articlesData?.articles || [];
  const total = articlesData?.total || 0;
  const sources = sourcesData?.sources || [];

  const handleSelectArticle = (article: any) => {
    selectArticle(article);
    toast.success('Article selected! Go to Translation page →');
  };

  const handleTranslateSelected = () => {
    if (selectedArticle) {
      navigate('/translation');
    } else {
      toast.error('Please select an article first');
    }
  };

  const handleStartScraper = () => {
    startScraper.mutate();
  };

  // Handle scraper completion - auto refresh articles
  const handleScraperComplete = useCallback((articlesCount: number) => {
    toast.success(`Scraping complete! Found ${articlesCount} articles`);
    // Clear the active job ID
    setActiveScraperJobId(null);
    // Refresh the articles list
    setTimeout(() => {
      refetch();
    }, 500);
  }, [setActiveScraperJobId, refetch]);

  // Handle banner close
  const handleBannerClose = useCallback(() => {
    setActiveScraperJobId(null);
  }, [setActiveScraperJobId]);

  return (
    <>
      {/* Real-time Scraper Status Banner */}
      <ScraperStatusBanner
        jobId={activeScraperJobId}
        onComplete={handleScraperComplete}
        onClose={handleBannerClose}
      />

      <div className={`max-w-7xl mx-auto px-4 py-8 ${activeScraperJobId ? 'pt-20' : ''}`}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          {jobId && (
            <button
              onClick={() => navigate('/articles')}
              className="text-teal-600 hover:text-teal-700"
            >
              ← Back to Latest
            </button>
          )}
          <h1 className="text-3xl font-bold text-gray-900">
            {jobId ? 'Historical Articles' : 'Travel Articles'}
          </h1>
        </div>
        <p className="text-gray-600">
          {jobId
            ? 'Viewing articles from a past scraping session'
            : 'Browse and select articles for translation'
          }
        </p>
      </div>

      {/* Actions Bar */}
      <div className="mb-6 flex flex-wrap gap-4">
        <button
          onClick={handleStartScraper}
          disabled={startScraper.isPending}
          className="px-6 py-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:opacity-50 transition-colors"
        >
          {startScraper.isPending ? 'Starting...' : '🔄 Start Scraper'}
        </button>

        <button
          onClick={() => refetch()}
          className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
        >
          🔃 Refresh
        </button>

        {selectedArticle && (
          <button
            onClick={handleTranslateSelected}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition-colors ml-auto"
          >
            ✨ Translate Selected →
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="mb-6 bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Filters</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search articles..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>

          {/* Sources */}
          <div>
            <SearchableMultiSelect
              label="Sources"
              placeholder="All sources"
              options={sources.map((s: any) => ({
                value: s.source,
                label: s.source,
                count: s.count,
              }))}
              selected={filters.sources}
              onChange={(selected) => setFilters({ sources: selected, page: 1 })}
            />
          </div>

          {/* Page Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Per Page
            </label>
            <select
              value={filters.pageSize}
              onChange={(e) => setFilters({ pageSize: parseInt(e.target.value), page: 1 })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>

        <button
          onClick={resetFilters}
          className="mt-4 text-teal-600 hover:text-teal-700 font-medium text-sm"
        >
          Clear all filters
        </button>
      </div>

      {/* Current Session Info - only show when viewing latest */}
      {!jobId && articlesData?.current_job && (
        <div className="mb-6 bg-teal-50 border border-teal-200 rounded-lg px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-teal-600 font-medium">Latest Scraping Session</span>
              <span className="text-gray-500">•</span>
              <span className="text-gray-600">
                {new Date(articlesData.current_job.completed_at).toLocaleString()}
              </span>
            </div>
            <button
              onClick={() => navigate('/scheduler')}
              className="text-teal-600 hover:text-teal-700 text-sm font-medium"
            >
              View All History →
            </button>
          </div>
        </div>
      )}

      {/* Historical Session Info - only show when viewing history */}
      {jobId && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-amber-700 font-medium">Historical Session</span>
              <span className="text-gray-500">•</span>
              <span className="text-gray-600">Session ID: {jobId}</span>
            </div>
            <button
              onClick={() => navigate('/scheduler')}
              className="text-amber-700 hover:text-amber-800 text-sm font-medium"
            >
              Back to History →
            </button>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="mb-6 text-gray-600">
        Showing {articles.length} of {total} articles{!jobId && ' from latest session'}
        {filters.search && ` • Filtered by: "${filters.search}"`}
      </div>

      {/* Articles Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          <p className="mt-4 text-gray-600">Loading articles...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <p className="text-gray-500 text-lg">No articles found</p>
          <button
            onClick={handleStartScraper}
            className="mt-4 px-6 py-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600"
          >
            Start Scraper
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {articles.map((article: any) => (
              <ArticleCard
                key={article.id || article.article_url || article.headline}
                article={article}
                isSelected={selectedArticle?.headline === article.headline}
                onSelect={() => handleSelectArticle(article)}
              />
            ))}
          </div>

          {/* Pagination */}
          {total > filters.pageSize && (
            <div className="mt-8 flex justify-center gap-2">
              <button
                onClick={() => setFilters({ page: filters.page - 1 })}
                disabled={filters.page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>

              <span className="px-4 py-2 text-gray-700">
                Page {filters.page} of {Math.ceil(total / filters.pageSize)}
              </span>

              <button
                onClick={() => setFilters({ page: filters.page + 1 })}
                disabled={filters.page >= Math.ceil(total / filters.pageSize)}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Floating action button for selected article */}
      {selectedArticle && (
        <button
          onClick={handleTranslateSelected}
          className="fixed bottom-8 right-8 px-8 py-4 bg-blue-500 text-white rounded-full font-bold shadow-lg hover:bg-blue-600 hover:shadow-xl transition-all transform hover:scale-105"
        >
          Translate Selected Article
        </button>
      )}
      </div>
    </>
  );
};
