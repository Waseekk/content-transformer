import { useState, useEffect } from 'react';
import { getArticles, getSources, type Article } from '../../api/articles';
import { Card, Badge, Spinner, Button } from '../common';
import toast from 'react-hot-toast';

export function ArticlesList() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadSources();
  }, []);

  useEffect(() => {
    loadArticles();
  }, [page, selectedSource]);

  const loadSources = async () => {
    try {
      const sourcesData = await getSources();
      setSources(sourcesData.map(s => s.source));
    } catch {
      // Failed to load sources - continue with empty list
    }
  };

  const loadArticles = async () => {
    setIsLoading(true);
    try {
      const response = await getArticles(
        page,
        10,
        selectedSource || undefined,
        searchQuery || undefined
      );
      setArticles(response.items);
      setTotalPages(response.pages);
      setTotal(response.total);
    } catch (error) {
      toast.error('Failed to load articles');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadArticles();
  };

  const handleClearFilters = () => {
    setSelectedSource('');
    setSearchQuery('');
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <Card>
        <div className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search articles..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="w-full md:w-48">
              <select
                value={selectedSource}
                onChange={(e) => {
                  setSelectedSource(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Sources</option>
                {sources.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </div>
            <Button variant="primary" onClick={handleSearch}>
              Search
            </Button>
            <Button variant="secondary" onClick={handleClearFilters}>
              Clear
            </Button>
          </div>

          <div className="text-sm text-gray-600">
            Showing {articles.length} of {total} articles
            {selectedSource && <span> from {selectedSource}</span>}
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : articles.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No articles found</p>
            <p className="text-gray-400 text-sm mt-2">
              Try adjusting your filters or run a scraper job to collect articles
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {articles.map((article) => (
            <Card key={article.id} className="hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="info" size="sm">
                      {article.source}
                    </Badge>
                    {article.published_date && (
                      <span className="text-xs text-gray-500">
                        {new Date(article.published_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {article.title}
                  </h3>
                  {article.content && (
                    <p className="text-gray-600 text-sm line-clamp-3 mb-3">
                      {article.content}
                    </p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 hover:underline"
                    >
                      View Original →
                    </a>
                    <span>Scraped: {new Date(article.scraped_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
