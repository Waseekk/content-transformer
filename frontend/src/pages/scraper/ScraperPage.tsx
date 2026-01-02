import { ScraperControls } from '../../components/scraper/ScraperControls';

export function ScraperPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Scraper</h1>
          <p className="text-gray-600 mt-2">
            Collect travel news articles from configured sources
          </p>
        </div>

        <ScraperControls />
      </div>
    </div>
  );
}
