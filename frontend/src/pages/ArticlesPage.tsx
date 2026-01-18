/**
 * Articles Page - Modern article listing with filters and selection
 */

import { useState, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useArticles, useArticleSources, useScrapingSessions } from '../hooks/useArticles';
import { useStartScraper } from '../hooks/useScraper';
import { useAppStore } from '../store/useAppStore';
import { ArticleCard } from '../components/common/ArticleCard';
import { SearchableMultiSelect } from '../components/common/SearchableMultiSelect';
import { ScraperStatusBanner } from '../components/common/ScraperStatusBanner';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  HiFilter,
  HiClock,
  HiRefresh,
  HiSearch,
  HiChevronLeft,
  HiChevronRight,
  HiSparkles,
  HiPlay,
  HiArrowRight,
  HiCollection,
  HiX,
  HiNewspaper
} from 'react-icons/hi';

export const ArticlesPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const jobIdParam = searchParams.get('job_id');
  const jobId = jobIdParam ? parseInt(jobIdParam) : undefined;

  const [showLatestOnly, setShowLatestOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const { data: articlesData, isLoading, refetch } = useArticles({
    latestOnly: jobId ? false : showLatestOnly,
    jobId: jobId,
  });
  const { data: sourcesData } = useArticleSources();
  const { data: sessionsData } = useScrapingSessions({ limit: 1 });
  const startScraper = useStartScraper();

  const latestSession = sessionsData?.sessions?.[0];

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
  const [knownJobId, setKnownJobId] = useState<number | null>(null);
  const [hasNewArticles, setHasNewArticles] = useState(false);

  useEffect(() => {
    const currentJobId = articlesData?.current_job?.job_id;
    if (currentJobId && !knownJobId) {
      setKnownJobId(currentJobId);
    }
  }, [articlesData?.current_job?.job_id, knownJobId]);

  useEffect(() => {
    if (jobId || !knownJobId) return;

    const checkForNewArticles = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/articles?latest_only=true&limit=1`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
          }
        );
        if (response.ok) {
          const data = await response.json();
          const latestJobId = data.current_job?.job_id;
          if (latestJobId && latestJobId !== knownJobId) {
            setHasNewArticles(true);
          }
        }
      } catch (error) {
        // Silently ignore polling errors
      }
    };

    const interval = setInterval(checkForNewArticles, 30000);
    return () => clearInterval(interval);
  }, [jobId, knownJobId]);

  const handleLoadNewArticles = useCallback(() => {
    setHasNewArticles(false);
    setKnownJobId(null);
    refetch();
  }, [refetch]);

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
    toast.success('Article selected! Go to Translation page');
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

  const handleScraperComplete = useCallback((articlesCount: number) => {
    toast.success(`Scraping complete! Found ${articlesCount} new articles.`);
    setActiveScraperJobId(null);
    setKnownJobId(null);
    refetch();
    queryClient.invalidateQueries({ queryKey: ['articleSources'] });
    queryClient.invalidateQueries({ queryKey: ['articleStats'] });
  }, [setActiveScraperJobId, refetch, queryClient]);

  const handleBannerClose = useCallback(() => {
    setActiveScraperJobId(null);
  }, [setActiveScraperJobId]);

  const totalPages = Math.ceil(total / filters.pageSize);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FAF8F5] to-[#F5F3F0]">
      {/* Real-time Scraper Status Banner */}
      <ScraperStatusBanner
        jobId={activeScraperJobId}
        onComplete={handleScraperComplete}
        onClose={handleBannerClose}
      />

      {/* New Articles Available Banner */}
      {hasNewArticles && (
        <div className="fixed top-0 left-0 right-0 z-40 bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <HiSparkles className="w-5 h-5" />
              <span className="font-medium">New articles available from scheduler!</span>
            </div>
            <button
              onClick={handleLoadNewArticles}
              className="px-4 py-1.5 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Load New Articles
            </button>
          </div>
        </div>
      )}

      <div className={`max-w-7xl mx-auto px-6 py-8 ${activeScraperJobId || hasNewArticles ? 'pt-20' : ''}`}>
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-4">
              {jobId && (
                <button
                  onClick={() => navigate('/articles')}
                  className="flex items-center gap-1 text-teal-600 hover:text-teal-700 font-medium"
                >
                  <HiChevronLeft className="w-5 h-5" />
                  Back to Latest
                </button>
              )}
              <h1 className="text-3xl font-bold text-gray-900">
                {jobId ? 'Historical Articles' : 'Articles'}
              </h1>
            </div>

            {/* Quick Stats */}
            <div className="hidden md:flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <HiCollection className="w-5 h-5" />
                <span><strong className="text-gray-900">{total}</strong> articles</span>
              </div>
              {latestSession && !jobId && (
                <div className="flex items-center gap-2 text-gray-500">
                  <HiClock className="w-5 h-5" />
                  <span>Last scraped {new Date(latestSession.completed_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
          <p className="text-gray-500">
            {jobId
              ? 'Viewing articles from a past scraping session'
              : 'Browse and select articles for translation'
            }
          </p>
        </div>

        {/* Actions Bar */}
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <button
            onClick={handleStartScraper}
            disabled={startScraper.isPending}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-teal-500 text-white rounded-xl font-semibold hover:bg-teal-600 disabled:opacity-50 transition-all shadow-sm hover:shadow-md"
          >
            <HiPlay className="w-5 h-5" />
            {startScraper.isPending ? 'Starting...' : 'Start Scraper'}
          </button>

          <button
            onClick={() => refetch()}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all border border-gray-200"
          >
            <HiRefresh className="w-5 h-5" />
            Refresh
          </button>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`
              inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all border
              ${showFilters
                ? 'bg-teal-50 text-teal-700 border-teal-200'
                : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
              }
            `}
          >
            <HiFilter className="w-5 h-5" />
            Filters
            {(filters.search || filters.sources.length > 0) && (
              <span className="w-2 h-2 bg-teal-500 rounded-full"></span>
            )}
          </button>

          {!jobId && (
            <button
              onClick={() => setShowLatestOnly(!showLatestOnly)}
              className={`
                inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold transition-all border
                ${showLatestOnly
                  ? 'bg-blue-50 text-blue-700 border-blue-200'
                  : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                }
              `}
            >
              <HiClock className="w-5 h-5" />
              {showLatestOnly ? 'Latest Only' : 'All Articles'}
            </button>
          )}

          {selectedArticle && (
            <button
              onClick={handleTranslateSelected}
              className="ml-auto inline-flex items-center gap-2 px-5 py-2.5 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-600 transition-all shadow-sm hover:shadow-md"
            >
              Translate Selected
              <HiArrowRight className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mb-6 bg-white rounded-2xl p-6 shadow-sm border border-gray-100 animate-in slide-in-from-top-2 duration-200">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
              <button
                onClick={resetFilters}
                className="text-sm text-gray-500 hover:text-gray-700 font-medium"
              >
                Clear all
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search
                </label>
                <div className="relative">
                  <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Search articles..."
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                  />
                </div>
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
            </div>
          </div>
        )}

        {/* Historical Session Banner */}
        {jobId && (
          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-2xl px-5 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <HiClock className="w-5 h-5 text-amber-600" />
                <span className="font-medium text-amber-800">Historical Session</span>
                <span className="text-amber-600">ID: {jobId}</span>
              </div>
              <button
                onClick={() => navigate('/scheduler')}
                className="text-amber-700 hover:text-amber-800 font-medium text-sm flex items-center gap-1"
              >
                View All History
                <HiArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Results info */}
        <div className="mb-5 flex items-center justify-between">
          <p className="text-gray-500 text-sm">
            Showing <strong className="text-gray-700">{articles.length}</strong> of <strong className="text-gray-700">{total}</strong> articles
            {!jobId && showLatestOnly && ' from latest session'}
            {filters.search && (
              <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded-full text-xs">
                "{filters.search}"
                <button onClick={() => setSearchInput('')} className="hover:text-gray-700">
                  <HiX className="w-3 h-3" />
                </button>
              </span>
            )}
          </p>

          {!jobId && (
            <button
              onClick={() => navigate('/scheduler')}
              className="text-sm text-teal-600 hover:text-teal-700 font-medium flex items-center gap-1"
            >
              View Scraping History
              <HiArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Articles Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-500 font-medium">Loading articles...</p>
          </div>
        ) : articles.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-gray-100">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <HiNewspaper className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No articles found</h3>
            <p className="text-gray-500 mb-6">Start the scraper to fetch new articles</p>
            <button
              onClick={handleStartScraper}
              disabled={startScraper.isPending}
              className="inline-flex items-center gap-2 px-6 py-3 bg-teal-500 text-white rounded-xl font-semibold hover:bg-teal-600 transition-all"
            >
              <HiPlay className="w-5 h-5" />
              Start Scraper
            </button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {articles.map((article: any) => (
                <ArticleCard
                  key={article.id || article.article_url || article.headline}
                  article={article}
                  isSelected={selectedArticle?.headline === article.headline}
                  onSelect={() => handleSelectArticle(article)}
                />
              ))}
            </div>

            {/* Pagination & Per Page */}
            <div className="mt-10 flex items-center justify-between">
              {/* Empty spacer for alignment */}
              <div className="w-32"></div>

              {/* Pagination - Center */}
              {totalPages > 1 ? (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setFilters({ page: filters.page - 1 })}
                    disabled={filters.page === 1}
                    className="p-2.5 rounded-xl border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-all disabled:cursor-not-allowed"
                  >
                    <HiChevronLeft className="w-5 h-5 text-gray-600" />
                  </button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (filters.page <= 3) {
                        pageNum = i + 1;
                      } else if (filters.page >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = filters.page - 2 + i;
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => setFilters({ page: pageNum })}
                          className={`
                            w-10 h-10 rounded-xl font-medium transition-all
                            ${filters.page === pageNum
                              ? 'bg-teal-500 text-white shadow-md'
                              : 'hover:bg-gray-100 text-gray-600'
                            }
                          `}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  <button
                    onClick={() => setFilters({ page: filters.page + 1 })}
                    disabled={filters.page >= totalPages}
                    className="p-2.5 rounded-xl border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-all disabled:cursor-not-allowed"
                  >
                    <HiChevronRight className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              ) : (
                <div></div>
              )}

              {/* Per Page - Right */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Per page:</span>
                <select
                  value={filters.pageSize}
                  onChange={(e) => setFilters({ pageSize: parseInt(e.target.value), page: 1 })}
                  className="px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all bg-white"
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>
          </>
        )}

        {/* Floating action button */}
        {selectedArticle && (
          <button
            onClick={handleTranslateSelected}
            className="fixed bottom-8 right-8 inline-flex items-center gap-3 px-6 py-4 bg-blue-500 text-white rounded-2xl font-bold shadow-xl hover:bg-blue-600 hover:shadow-2xl transition-all transform hover:scale-105"
          >
            <span>Translate Article</span>
            <HiArrowRight className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
};
