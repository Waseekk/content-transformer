/**
 * Google News Search Tab Component
 * Search Google News with keyword, time filter, and pagination
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiSearch,
  HiClock,
  HiExternalLink,
  HiChevronLeft,
  HiChevronRight,
  HiRefresh,
  HiNewspaper,
  HiGlobe,
  HiLightningBolt
} from 'react-icons/hi';
import { useGoogleNewsSearch, usePaginatedGoogleNewsSearch } from '../../hooks/useGoogleNewsSearch';
import type { GoogleNewsResult } from '../../services/api';

const TIME_FILTER_OPTIONS = [
  { value: '1h', label: 'Past hour' },
  { value: '24h', label: 'Past 24 hours' },
  { value: '7d', label: 'Past week' },
  { value: '30d', label: 'Past month' },
];

export const GoogleNewsSearchTab = () => {
  const [keyword, setKeyword] = useState('');
  const [timeFilter, setTimeFilter] = useState('24h');
  const [page, setPage] = useState(1);
  const [limit] = useState(10);

  // Track if we have performed a search
  const [hasSearched, setHasSearched] = useState(false);
  const [searchedKeyword, setSearchedKeyword] = useState('');
  const [searchedTimeFilter, setSearchedTimeFilter] = useState('');

  const searchMutation = useGoogleNewsSearch();

  // Paginated results query
  const {
    data: paginatedData,
    isLoading: isPaginatedLoading,
  } = usePaginatedGoogleNewsSearch(
    searchedKeyword,
    searchedTimeFilter,
    page,
    limit,
    hasSearched && !!searchedKeyword
  );

  // Reset page when search parameters change
  useEffect(() => {
    setPage(1);
  }, [searchedKeyword, searchedTimeFilter]);

  const handleSearch = async () => {
    if (!keyword.trim()) return;

    setHasSearched(true);
    setSearchedKeyword(keyword.trim());
    setSearchedTimeFilter(timeFilter);
    setPage(1);

    console.log('Starting search for:', keyword.trim(), timeFilter);

    try {
      const result = await searchMutation.mutateAsync({
        keyword: keyword.trim(),
        time_filter: timeFilter,
        max_results: 50,
      });
      console.log('Search result:', result);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const isLoading = searchMutation.isPending || isPaginatedLoading;

  // Get all results from mutation (fresh search) or paginated data
  const allResults = searchMutation.data?.results || [];
  const paginatedResults = paginatedData?.results || [];

  // Calculate total and pages
  const totalResults = searchMutation.data?.total_results || paginatedData?.total || 0;
  const totalPages = Math.ceil(totalResults / limit) || paginatedData?.total_pages || 0;
  const isCached = searchMutation.data?.cached || paginatedData?.cached || false;

  // Apply client-side pagination to mutation results, or use server-paginated results
  const results = allResults.length > 0
    ? allResults.slice((page - 1) * limit, page * limit)
    : paginatedResults;

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Keyword Input */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Keyword
            </label>
            <div className="relative">
              <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., sylhet, bangladesh tourism, travel news..."
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all text-lg"
              />
            </div>
          </div>

          {/* Time Filter */}
          <div className="w-full md:w-48">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Range
            </label>
            <div className="relative">
              <HiClock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all appearance-none bg-white cursor-pointer"
              >
                {TIME_FILTER_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Button */}
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={isLoading || !keyword.trim()}
              className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-teal-500 to-teal-600 text-white rounded-xl font-semibold hover:from-teal-600 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <HiSearch className="w-5 h-5" />
                  Search News
                </>
              )}
            </button>
          </div>
        </div>

        {/* Search Info */}
        {hasSearched && searchMutation.data && (
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <HiLightningBolt className="w-4 h-4" />
              {searchMutation.data.search_time_ms}ms
            </span>
            {isCached && (
              <span className="flex items-center gap-1 text-blue-600">
                <HiRefresh className="w-4 h-4" />
                Cached results
              </span>
            )}
            <span>
              Showing results for "<strong>{searchedKeyword}</strong>"
            </span>
          </div>
        )}
      </div>

      {/* Results */}
      {hasSearched && (
        <div className="space-y-4">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <p className="text-gray-500">
              Found <strong className="text-gray-900">{totalResults}</strong> news articles
            </p>
            {totalResults > 0 && (
              <p className="text-sm text-gray-400">
                Page {page} of {totalPages}
              </p>
            )}
          </div>

          {/* Results List */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-gray-100">
              <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-500 font-medium">Searching news...</p>
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-gray-100">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <HiNewspaper className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-500">Try a different keyword or time range</p>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={`${searchedKeyword}-${page}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="space-y-3"
              >
                {results.map((result: GoogleNewsResult, index: number) => (
                  <NewsResultCard key={`${result.url}-${index}`} result={result} />
                ))}
              </motion.div>
            </AnimatePresence>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1 || isLoading}
                className="p-2.5 rounded-xl border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-all disabled:cursor-not-allowed"
              >
                <HiChevronLeft className="w-5 h-5 text-gray-600" />
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = page - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      disabled={isLoading}
                      className={`
                        w-10 h-10 rounded-xl font-medium transition-all
                        ${page === pageNum
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
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages || isLoading}
                className="p-2.5 rounded-xl border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-all disabled:cursor-not-allowed"
              >
                <HiChevronRight className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Initial State */}
      {!hasSearched && (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-gray-100">
          <div className="w-20 h-20 bg-gradient-to-br from-teal-100 to-blue-100 rounded-full flex items-center justify-center mb-6">
            <HiGlobe className="w-10 h-10 text-teal-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Search News</h3>
          <p className="text-gray-500 text-center max-w-md">
            Enter a keyword to find recent news articles. Results are filtered by time and cached for 5 minutes.
          </p>
        </div>
      )}
    </div>
  );
};

/**
 * Individual news result card
 */
const NewsResultCard = ({ result }: { result: GoogleNewsResult }) => {
  return (
    <motion.a
      href={result.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white rounded-xl border border-gray-100 p-5 hover:border-teal-200 hover:shadow-md transition-all group"
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="font-semibold text-gray-900 group-hover:text-teal-600 transition-colors line-clamp-2 mb-2">
            {result.title}
          </h3>

          {/* Snippet */}
          {result.snippet && (
            <p className="text-gray-500 text-sm line-clamp-2 mb-3">
              {result.snippet}
            </p>
          )}

          {/* Meta Info */}
          <div className="flex items-center gap-3 text-xs text-gray-400">
            {result.source && (
              <span className="font-medium text-gray-600">{result.source}</span>
            )}
            {result.published_time && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <HiClock className="w-3 h-3" />
                  {result.published_time}
                </span>
              </>
            )}
          </div>
        </div>

        {/* External Link Icon */}
        <div className="flex-shrink-0 p-2 bg-gray-50 rounded-lg group-hover:bg-teal-50 transition-colors">
          <HiExternalLink className="w-5 h-5 text-gray-400 group-hover:text-teal-600 transition-colors" />
        </div>
      </div>
    </motion.a>
  );
};

export default GoogleNewsSearchTab;
