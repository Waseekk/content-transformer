import { ArticlesList } from '../../components/articles/ArticlesList';

export function ArticlesPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Articles</h1>
          <p className="text-gray-600 mt-2">
            Browse and search scraped travel news articles
          </p>
        </div>

        <ArticlesList />
      </div>
    </div>
  );
}
