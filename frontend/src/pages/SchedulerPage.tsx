/**
 * Scheduler Page - Modern Scraper & Scheduler Control Center
 */

import { useState, useCallback } from 'react';
import {
  HiPlay,
  HiStop,
  HiRefresh,
  HiClock,
  HiCalendar,
  HiChartBar,
  HiCheckCircle,
  HiLightningBolt,
} from 'react-icons/hi';
import {
  useSchedulerStatus,
  useStartScheduler,
  useStopScheduler,
  useSchedulerHistory,
} from '../hooks/useScheduler';
import { useStartScraper } from '../hooks/useScraper';
import { useArticleStats, useScrapingSessions } from '../hooks/useArticles';
import { useAppStore } from '../store/useAppStore';
import { ScraperStatusBanner } from '../components/common/ScraperStatusBanner';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

// Interval presets
const INTERVAL_PRESETS = [
  { value: 1, label: '1 hour', description: 'High frequency' },
  { value: 2, label: '2 hours', description: 'Frequent' },
  { value: 4, label: '4 hours', description: 'Regular' },
  { value: 6, label: '6 hours', description: '4x daily' },
  { value: 12, label: '12 hours', description: '2x daily' },
  { value: 24, label: '24 hours', description: 'Daily' },
];

export const SchedulerPage = () => {
  const navigate = useNavigate();
  const { data: status } = useSchedulerStatus();
  useSchedulerHistory(10); // Keep the query active for caching
  const { data: stats, refetch: refetchStats } = useArticleStats();
  const { data: scrapingSessions, isLoading: sessionsLoading, refetch: refetchSessions } = useScrapingSessions({ limit: 20 });
  const startScheduler = useStartScheduler();
  const stopScheduler = useStopScheduler();
  const startScraper = useStartScraper();

  // Global state for scraper job tracking
  const { activeScraperJobId, setActiveScraperJobId } = useAppStore();

  // Local state
  const [scheduleMode, setScheduleMode] = useState<'preset' | 'custom'>('preset');
  const [selectedPreset, setSelectedPreset] = useState(6);
  const [customHours, setCustomHours] = useState(0);
  const [customMinutes, setCustomMinutes] = useState(30);
  const [activeTab, setActiveTab] = useState<'scheduler' | 'scraper' | 'history'>('scheduler');

  const isRunning = status?.is_running || false;

  // Handle scraper completion
  const handleScraperComplete = useCallback((articlesCount: number) => {
    toast.success(`Scraping complete! Found ${articlesCount} articles`);
    setActiveScraperJobId(null);
    // Refresh stats and sessions
    refetchStats();
    refetchSessions();
  }, [setActiveScraperJobId, refetchStats, refetchSessions]);

  const handleBannerClose = useCallback(() => {
    setActiveScraperJobId(null);
  }, [setActiveScraperJobId]);

  // Get effective interval in hours
  const getIntervalHours = () => {
    if (scheduleMode === 'preset') {
      return selectedPreset;
    }
    return customHours + customMinutes / 60;
  };

  const handleStartScheduler = () => {
    const intervalHours = getIntervalHours();
    if (intervalHours < 0.0167) { // 1 minute minimum for testing
      toast.error('Minimum interval is 1 minute');
      return;
    }
    startScheduler.mutate(intervalHours);
  };

  const handleStopScheduler = () => {
    stopScheduler.mutate();
  };

  const handleRunNow = () => {
    startScraper.mutate();
  };

  // Format time until next run
  const formatTimeUntil = (timeStr: string | null) => {
    if (!timeStr) return 'N/A';
    return timeStr;
  };

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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Control Center
        </h1>
        <p className="text-gray-600">
          Manage scraping and automated scheduling
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <HiChartBar className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Total Articles</p>
              <p className="text-xl font-bold text-gray-900">{stats?.total_articles || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <HiCalendar className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Last 7 Days</p>
              <p className="text-xl font-bold text-gray-900">{stats?.last_7_days || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isRunning ? 'bg-green-100' : 'bg-gray-100'}`}>
              <HiClock className={`w-5 h-5 ${isRunning ? 'text-green-600' : 'text-gray-600'}`} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Scheduler</p>
              <p className={`text-xl font-bold ${isRunning ? 'text-green-600' : 'text-gray-600'}`}>
                {isRunning ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <HiRefresh className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Total Runs</p>
              <p className="text-xl font-bold text-gray-900">{status?.run_count || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {[
          { id: 'scheduler', label: 'Scheduler', icon: HiClock },
          { id: 'scraper', label: 'Run Now', icon: HiLightningBolt },
          { id: 'history', label: 'History', icon: HiChartBar },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`
              flex items-center gap-2 px-4 py-3 font-medium transition-all border-b-2 -mb-[2px]
              ${activeTab === tab.id
                ? 'text-teal-600 border-teal-500'
                : 'text-gray-500 border-transparent hover:text-gray-700'
              }
            `}
          >
            <tab.icon className="w-5 h-5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'scheduler' && (
        <div className="space-y-6">
          {/* Status Card */}
          <div className={`
            rounded-xl p-6 border-2 transition-all
            ${isRunning
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300'
              : 'bg-white border-gray-200'
            }
          `}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className={`
                  w-14 h-14 rounded-full flex items-center justify-center
                  ${isRunning ? 'bg-green-100' : 'bg-gray-100'}
                `}>
                  {isRunning ? (
                    <div className="relative">
                      <HiPlay className="w-7 h-7 text-green-600" />
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    </div>
                  ) : (
                    <HiStop className="w-7 h-7 text-gray-400" />
                  )}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {isRunning ? 'Scheduler Running' : 'Scheduler Stopped'}
                  </h3>
                  {isRunning && status && (
                    <p className="text-sm text-gray-600 mt-1">
                      Running every <span className="font-semibold text-teal-600">{status.interval_hours}h</span>
                      {' | '}Next run in <span className="font-semibold text-teal-600">{formatTimeUntil(status.time_until_next)}</span>
                    </p>
                  )}
                  {!isRunning && (
                    <p className="text-sm text-gray-500 mt-1">Configure and start the scheduler below</p>
                  )}
                </div>
              </div>

              <div className="flex gap-3">
                {isRunning ? (
                  <button
                    onClick={handleStopScheduler}
                    disabled={stopScheduler.isPending}
                    className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg font-semibold transition-all disabled:opacity-50 flex items-center gap-2"
                  >
                    <HiStop className="w-5 h-5" />
                    {stopScheduler.isPending ? 'Stopping...' : 'Stop'}
                  </button>
                ) : (
                  <button
                    onClick={handleStartScheduler}
                    disabled={startScheduler.isPending}
                    className="px-6 py-3 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-semibold transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg hover:shadow-xl"
                  >
                    <HiPlay className="w-5 h-5" />
                    {startScheduler.isPending ? 'Starting...' : 'Start Scheduler'}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Configuration */}
          {!isRunning && (
            <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Configure Interval
              </h3>

              {/* Mode Toggle */}
              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setScheduleMode('preset')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    scheduleMode === 'preset'
                      ? 'bg-teal-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Preset Intervals
                </button>
                <button
                  onClick={() => setScheduleMode('custom')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    scheduleMode === 'custom'
                      ? 'bg-teal-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Custom Time
                </button>
              </div>

              {scheduleMode === 'preset' ? (
                /* Preset Intervals */
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  {INTERVAL_PRESETS.map((preset) => (
                    <button
                      key={preset.value}
                      onClick={() => setSelectedPreset(preset.value)}
                      className={`
                        p-4 rounded-xl border-2 transition-all text-center
                        ${selectedPreset === preset.value
                          ? 'border-teal-500 bg-teal-50 shadow-md'
                          : 'border-gray-200 bg-white hover:border-teal-300 hover:bg-gray-50'
                        }
                      `}
                    >
                      <p className="text-2xl font-bold text-teal-600 mb-1">{preset.value}h</p>
                      <p className="text-xs text-gray-500">{preset.description}</p>
                    </button>
                  ))}
                </div>
              ) : (
                /* Custom Time */
                <div className="max-w-md">
                  <p className="text-sm text-gray-600 mb-4">
                    Set a custom interval (minimum 1 minute)
                  </p>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">Hours</label>
                      <input
                        type="number"
                        min="0"
                        max="72"
                        value={customHours}
                        onChange={(e) => setCustomHours(Math.max(0, parseInt(e.target.value) || 0))}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-xl font-semibold focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                    <span className="text-2xl font-bold text-gray-400 pt-5">:</span>
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">Minutes</label>
                      <input
                        type="number"
                        min="0"
                        max="59"
                        value={customMinutes}
                        onChange={(e) => setCustomMinutes(Math.min(59, Math.max(0, parseInt(e.target.value) || 0)))}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-xl font-semibold focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-3">
                    Scraper will run every <span className="font-semibold text-teal-600">
                      {customHours > 0 ? `${customHours}h ` : ''}{customMinutes > 0 ? `${customMinutes}m` : ''}
                      {customHours === 0 && customMinutes === 0 && '0m'}
                    </span>
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'scraper' && (
        <div className="space-y-6">
          {/* Manual Scraper */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-gradient-to-br from-orange-100 to-amber-100 rounded-xl">
                <HiLightningBolt className="w-8 h-8 text-orange-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Run Scraper Now</h3>
                <p className="text-sm text-gray-600">
                  Manually trigger the scraper to fetch latest articles
                </p>
              </div>
            </div>

            <button
              onClick={handleRunNow}
              disabled={startScraper.isPending}
              className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl font-bold text-lg transition-all disabled:opacity-50 shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              {startScraper.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white" />
                  Running...
                </>
              ) : (
                <>
                  <HiRefresh className="w-6 h-6" />
                  Start Scraping
                </>
              )}
            </button>

            <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-sm text-amber-800">
                <strong>Note:</strong> This will scrape all enabled sources immediately.
                The process runs in the background and may take a few minutes to complete.
              </p>
            </div>
          </div>

          {/* Scraper Info */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Enabled Sources</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['tourism_review', 'independent_travel', 'newsuk_travel'].map((source) => (
                <div key={source} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <HiCheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{source.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* Info Banner */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> The Articles page shows only the latest scraping session.
              Past sessions are listed below - click "View Articles" to browse articles from any session.
            </p>
          </div>

          {/* Scraping Sessions List */}
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Past Scraping Sessions</h3>

            {sessionsLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500 mx-auto"></div>
                <p className="text-gray-500 mt-4">Loading sessions...</p>
              </div>
            ) : scrapingSessions?.sessions && scrapingSessions.sessions.length > 0 ? (
              <div className="space-y-3">
                {scrapingSessions.sessions.map((session: any) => (
                  <div
                    key={session.job_id}
                    className="flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-all"
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-green-100 rounded-full">
                        <HiCheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {session.completed_at
                            ? new Date(session.completed_at).toLocaleDateString('en-US', {
                                weekday: 'short',
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : 'Unknown date'
                          }
                        </p>
                        <p className="text-sm text-gray-500">
                          <span className="font-semibold text-teal-600">{session.article_count}</span> articles scraped
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => navigate(`/articles?job_id=${session.job_id}`)}
                      className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      View Articles
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <HiClock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No past sessions</p>
                <p className="text-sm mt-1">Run the scraper multiple times to build history</p>
              </div>
            )}

            {/* Pagination info */}
            {scrapingSessions?.total > 0 && (
              <p className="text-sm text-gray-500 mt-4 text-center">
                Showing {scrapingSessions.sessions.length} of {scrapingSessions.total} past sessions
              </p>
            )}
          </div>
        </div>
      )}
      </div>
    </>
  );
};
