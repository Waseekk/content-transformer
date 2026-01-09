/**
 * Dashboard Page - Overview with stats and quick actions
 */

import { useNavigate } from 'react-router-dom';
import { useArticleStats } from '../hooks/useArticles';
import { useSchedulerStatus } from '../hooks/useScheduler';
import { useAppStore } from '../store/useAppStore';
import { HiNewspaper, HiTranslate, HiClock, HiLightningBolt } from 'react-icons/hi';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const { data: stats } = useArticleStats();
  const { data: schedulerStatus } = useSchedulerStatus();
  const { selectedArticle } = useAppStore();

  const quickActions = [
    {
      title: 'Browse Articles',
      description: 'View and select articles for translation',
      icon: <HiNewspaper className="w-8 h-8" />,
      color: 'from-blue-500 to-blue-600',
      onClick: () => navigate('/articles'),
    },
    {
      title: 'Translate Article',
      description: selectedArticle
        ? 'Continue with selected article'
        : 'Select an article first',
      icon: <HiTranslate className="w-8 h-8" />,
      color: 'from-teal-500 to-teal-600',
      onClick: () => navigate(selectedArticle ? '/translation' : '/articles'),
      disabled: !selectedArticle,
    },
    {
      title: 'Scheduler',
      description: 'Configure automated scraping',
      icon: <HiClock className="w-8 h-8" />,
      color: 'from-purple-500 to-purple-600',
      onClick: () => navigate('/scheduler'),
    },
    {
      title: 'Start Scraper',
      description: 'Manually trigger news scraping',
      icon: <HiLightningBolt className="w-8 h-8" />,
      color: 'from-orange-500 to-orange-600',
      onClick: () => navigate('/articles'),
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📊 Dashboard
        </h1>
        <p className="text-gray-600">
          Welcome to Swiftor - Hard News & Soft News Platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Articles */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">📰</span>
            <HiNewspaper className="w-8 h-8 opacity-50" />
          </div>
          <p className="text-4xl font-bold mb-1">
            {stats?.total_articles?.toLocaleString() || '0'}
          </p>
          <p className="text-blue-100 text-sm">Total Articles</p>
        </div>

        {/* Available Sources */}
        <div className="bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">🌐</span>
            <HiNewspaper className="w-8 h-8 opacity-50" />
          </div>
          <p className="text-4xl font-bold mb-1">
            {stats?.total_sources || '0'}
          </p>
          <p className="text-teal-100 text-sm">News Sources</p>
        </div>

        {/* Recent Articles */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">🆕</span>
            <HiClock className="w-8 h-8 opacity-50" />
          </div>
          <p className="text-4xl font-bold mb-1">
            {stats?.recent_24h || '0'}
          </p>
          <p className="text-purple-100 text-sm">Last 24 Hours</p>
        </div>

        {/* Scheduler Status */}
        <div
          className={`
            rounded-xl p-6 text-white shadow-lg
            ${
              schedulerStatus?.is_running
                ? 'bg-gradient-to-br from-green-500 to-green-600'
                : 'bg-gradient-to-br from-gray-500 to-gray-600'
            }
          `}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-3xl">
              {schedulerStatus?.is_running ? '✓' : '⏸️'}
            </span>
            <HiClock className="w-8 h-8 opacity-50" />
          </div>
          <p className="text-2xl font-bold mb-1">
            {schedulerStatus?.is_running ? 'Active' : 'Inactive'}
          </p>
          <p className="text-sm opacity-90">
            {schedulerStatus?.is_running
              ? `Every ${schedulerStatus.interval_hours}h`
              : 'Scheduler'}
          </p>
        </div>
      </div>

      {/* Selected Article Banner */}
      {selectedArticle && (
        <div className="mb-8 bg-gradient-to-r from-teal-50 to-blue-50 rounded-xl p-6 border-2 border-teal-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-teal-700 mb-1">
                ✓ ARTICLE SELECTED
              </p>
              <p className="text-lg font-bold text-gray-900 mb-1">
                {selectedArticle.headline}
              </p>
              <p className="text-sm text-gray-600">
                {selectedArticle.publisher} • {selectedArticle.published_time}
              </p>
            </div>
            <button
              onClick={() => navigate('/translation')}
              className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-semibold transition-colors"
            >
              Translate Now →
            </button>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          ⚡ Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              onClick={action.onClick}
              disabled={action.disabled}
              className={`
                p-6 rounded-xl text-left transition-all transform hover:scale-105
                bg-gradient-to-br ${action.color} text-white shadow-lg
                hover:shadow-xl
                ${action.disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <div className="mb-4">{action.icon}</div>
              <h3 className="text-lg font-bold mb-2">{action.title}</h3>
              <p className="text-sm opacity-90">{action.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Workflow Guide */}
      <div className="bg-white rounded-xl p-8 border-2 border-gray-200 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          📋 Workflow Guide
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Step 1 */}
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              1
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">
              Browse Articles
            </h3>
            <p className="text-sm text-gray-600">
              View scraped articles from multiple news sources
            </p>
          </div>

          {/* Arrow */}
          <div className="hidden md:flex items-center justify-center">
            <span className="text-3xl text-gray-300">→</span>
          </div>

          {/* Step 2 */}
          <div className="text-center">
            <div className="w-16 h-16 bg-teal-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              2
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">
              Translate Content
            </h3>
            <p className="text-sm text-gray-600">
              Paste article content and translate to Bengali
            </p>
          </div>

          {/* Arrow */}
          <div className="hidden md:flex items-center justify-center">
            <span className="text-3xl text-gray-300">→</span>
          </div>

          {/* Step 3 */}
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-500 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              3
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">
              Generate Formats
            </h3>
            <p className="text-sm text-gray-600">
              Create multi-format content variations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
