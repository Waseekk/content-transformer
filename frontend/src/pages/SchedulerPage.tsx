/**
 * Scheduler Page - Premium Control Center for Scraping & Scheduling
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQueryClient } from '@tanstack/react-query';
import {
  HiPlay,
  HiStop,
  HiRefresh,
  HiClock,
  HiCalendar,
  HiChartBar,
  HiCheckCircle,
  HiLightningBolt,
  HiTrash,
  HiExclamation,
  HiCollection,
  HiArrowRight,
  HiCog,
} from 'react-icons/hi';
import {
  useSchedulerStatus,
  useStartScheduler,
  useStopScheduler,
  useSchedulerHistory,
} from '../hooks/useScheduler';
import { useStartScraper } from '../hooks/useScraper';
import { useArticleStats, useScrapingSessions, useDeleteSession, useDeleteAllHistory } from '../hooks/useArticles';
import { useAppStore } from '../store/useAppStore';
import { ScraperStatusBanner } from '../components/common/ScraperStatusBanner';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AnimatedCard, AILoader, GlowButton } from '../components/ui';

// Interval presets
const INTERVAL_PRESETS = [
  { value: 1, label: '1h', description: 'Hourly' },
  { value: 2, label: '2h', description: 'Frequent' },
  { value: 4, label: '4h', description: 'Regular' },
  { value: 6, label: '6h', description: '4x daily' },
  { value: 12, label: '12h', description: '2x daily' },
  { value: 24, label: '24h', description: 'Daily' },
];

export const SchedulerPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: status } = useSchedulerStatus();
  useSchedulerHistory(10);
  const { data: stats, refetch: refetchStats } = useArticleStats();

  const isSchedulerActive = status?.is_running || false;
  const schedulerIntervalMs = status?.interval_hours
    ? (status.interval_hours * 60 * 60 * 1000) + 10000
    : false;
  const smartRefetchInterval = isSchedulerActive ? schedulerIntervalMs : false;

  const { data: scrapingSessions, isLoading: sessionsLoading, refetch: refetchSessions } = useScrapingSessions(
    { limit: 20 },
    { refetchInterval: smartRefetchInterval }
  );
  const startScheduler = useStartScheduler();
  const stopScheduler = useStopScheduler();
  const startScraper = useStartScraper();
  const deleteSession = useDeleteSession();
  const deleteAllHistory = useDeleteAllHistory();

  const { activeScraperJobId, setActiveScraperJobId } = useAppStore();

  const [scheduleMode, setScheduleMode] = useState<'preset' | 'custom'>('preset');
  const [selectedPreset, setSelectedPreset] = useState(6);
  const [customHours, setCustomHours] = useState(0);
  const [customMinutes, setCustomMinutes] = useState(30);
  const [activeTab, setActiveTab] = useState<'scheduler' | 'scraper' | 'history'>('scheduler');

  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<number | null>(null);

  const isRunning = status?.is_running || false;

  const handleScraperComplete = useCallback((articlesCount: number) => {
    toast.success(`Scraping complete! Found ${articlesCount} articles`);
    setActiveScraperJobId(null);
    refetchStats();
    refetchSessions();
    queryClient.invalidateQueries({ queryKey: ['articleSources'] });
  }, [setActiveScraperJobId, refetchStats, refetchSessions, queryClient]);

  const handleBannerClose = useCallback(() => {
    setActiveScraperJobId(null);
  }, [setActiveScraperJobId]);

  const getIntervalHours = () => {
    if (scheduleMode === 'preset') {
      return selectedPreset;
    }
    return customHours + customMinutes / 60;
  };

  const handleStartScheduler = () => {
    const intervalHours = getIntervalHours();
    const intervalMinutes = Math.round(intervalHours * 60);
    if (intervalMinutes < 1) {
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

  const handleDeleteSession = (jobId: number) => {
    setSessionToDelete(jobId);
  };

  const confirmDeleteSession = () => {
    if (sessionToDelete) {
      deleteSession.mutate(sessionToDelete);
      setSessionToDelete(null);
    }
  };

  const handleDeleteAll = () => {
    setShowDeleteAllConfirm(true);
  };

  const confirmDeleteAll = () => {
    deleteAllHistory.mutate();
    setShowDeleteAllConfirm(false);
  };

  const formatTimeUntil = (timeStr: string | null) => {
    if (!timeStr) return 'N/A';
    return timeStr;
  };

  const formatInterval = (hours: number | null) => {
    if (!hours) return 'N/A';
    const totalMinutes = Math.round(hours * 60);
    const h = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    if (h > 0 && m > 0) return `${h}h ${m}m`;
    if (h > 0) return `${h}h`;
    return `${m}m`;
  };

  const tabs = [
    { id: 'scheduler', label: 'Scheduler', icon: HiCog },
    { id: 'scraper', label: 'Run Now', icon: HiLightningBolt },
    { id: 'history', label: 'History', icon: HiClock },
  ];

  return (
    <div className="min-h-screen ai-gradient-bg">
      {/* Real-time Scraper Status Banner */}
      <ScraperStatusBanner
        jobId={activeScraperJobId}
        onComplete={handleScraperComplete}
        onClose={handleBannerClose}
      />

      <div className={`max-w-6xl mx-auto px-6 py-8 ${activeScraperJobId ? 'pt-20' : ''}`}>
        {/* Hero Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-glow-purple"
          >
            <HiCog className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Control <span className="text-gradient">Center</span>
          </h1>
          <p className="text-gray-500 text-lg">
            Manage scraping automation and view history
          </p>
        </motion.div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon: HiCollection, label: 'Total Articles', value: stats?.total_articles || 0, color: 'blue' },
            { icon: HiCalendar, label: 'Last 7 Days', value: stats?.last_7_days || 0, color: 'green' },
            { icon: HiClock, label: 'Scheduler', value: isRunning ? 'Active' : 'Off', color: isRunning ? 'emerald' : 'gray', isStatus: true },
            { icon: HiChartBar, label: 'Total Runs', value: status?.run_count || 0, color: 'purple' },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="premium-card p-5"
            >
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${stat.color}-100`}>
                  <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className={`text-2xl font-bold ${stat.isStatus && isRunning ? 'text-emerald-600' : stat.isStatus ? 'text-gray-500' : 'text-gray-900'}`}>
                    {stat.value}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex gap-1 mb-6 glass-card rounded-2xl p-1.5 w-fit"
        >
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all
                ${activeTab === tab.id
                  ? 'bg-gradient-to-r from-ai-primary to-ai-secondary text-white shadow-glow-sm'
                  : 'text-gray-600 hover:bg-gray-100'
                }
              `}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </motion.button>
          ))}
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'scheduler' && (
            <motion.div
              key="scheduler"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* Status Card */}
              <AnimatedCard
                variant={isRunning ? 'glow' : 'default'}
                className={`p-6 ${isRunning ? 'bg-gradient-to-r from-emerald-50 to-teal-50' : ''}`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="flex items-center gap-5">
                    <motion.div
                      animate={isRunning ? { scale: [1, 1.05, 1] } : {}}
                      transition={{ duration: 2, repeat: Infinity }}
                      className={`
                        w-16 h-16 rounded-2xl flex items-center justify-center
                        ${isRunning
                          ? 'bg-gradient-to-br from-emerald-400 to-teal-500 shadow-lg'
                          : 'bg-gray-100'
                        }
                      `}
                    >
                      {isRunning ? (
                        <div className="relative">
                          <HiPlay className="w-8 h-8 text-white" />
                          <motion.span
                            animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                            className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full"
                          />
                        </div>
                      ) : (
                        <HiStop className="w-8 h-8 text-gray-400" />
                      )}
                    </motion.div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {isRunning ? 'Scheduler Running' : 'Scheduler Stopped'}
                      </h3>
                      {isRunning && status && (
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                          <span className="flex items-center gap-1.5">
                            <HiRefresh className="w-4 h-4 text-ai-primary" />
                            Every <strong className="text-ai-primary">{formatInterval(status.interval_hours)}</strong>
                          </span>
                          <span className="flex items-center gap-1.5">
                            <HiClock className="w-4 h-4 text-ai-primary" />
                            Next in <strong className="text-ai-primary">{formatTimeUntil(status.time_until_next)}</strong>
                          </span>
                        </div>
                      )}
                      {!isRunning && (
                        <p className="text-sm text-gray-500 mt-1">Configure interval below and start</p>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-3">
                    {isRunning ? (
                      <GlowButton
                        onClick={handleStopScheduler}
                        disabled={stopScheduler.isPending}
                        loading={stopScheduler.isPending}
                        variant="secondary"
                        icon={<HiStop className="w-5 h-5" />}
                        className="!bg-red-50 !text-red-600 !border-red-200 hover:!bg-red-100"
                      >
                        Stop
                      </GlowButton>
                    ) : (
                      <GlowButton
                        onClick={handleStartScheduler}
                        disabled={startScheduler.isPending}
                        loading={startScheduler.isPending}
                        icon={<HiPlay className="w-5 h-5" />}
                      >
                        Start Scheduler
                      </GlowButton>
                    )}
                  </div>
                </div>
              </AnimatedCard>

              {/* Configuration */}
              {!isRunning && (
                <AnimatedCard delay={0.1} className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-5">
                    Configure Interval
                  </h3>

                  {/* Mode Toggle */}
                  <div className="flex gap-2 mb-6">
                    {['preset', 'custom'].map((mode) => (
                      <motion.button
                        key={mode}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setScheduleMode(mode as any)}
                        className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                          scheduleMode === mode
                            ? 'bg-gradient-to-r from-ai-primary to-ai-secondary text-white shadow-glow-sm'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {mode === 'preset' ? 'Presets' : 'Custom'}
                      </motion.button>
                    ))}
                  </div>

                  {scheduleMode === 'preset' ? (
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                      {INTERVAL_PRESETS.map((preset, index) => (
                        <motion.button
                          key={preset.value}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setSelectedPreset(preset.value)}
                          className={`
                            p-4 rounded-xl border-2 transition-all text-center
                            ${selectedPreset === preset.value
                              ? 'border-ai-primary bg-ai-primary/10 shadow-glow-sm'
                              : 'border-gray-200 bg-white hover:border-ai-primary/50 hover:bg-gray-50'
                            }
                          `}
                        >
                          <p className={`text-2xl font-bold ${selectedPreset === preset.value ? 'text-ai-primary' : 'text-gray-700'}`}>
                            {preset.label}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">{preset.description}</p>
                        </motion.button>
                      ))}
                    </div>
                  ) : (
                    <div className="max-w-sm">
                      <p className="text-sm text-gray-500 mb-4">
                        Set a custom interval (minimum 1 minute)
                      </p>
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 mb-1.5">Hours</label>
                          <input
                            type="number"
                            min="0"
                            max="72"
                            value={customHours}
                            onChange={(e) => setCustomHours(Math.max(0, parseInt(e.target.value) || 0))}
                            className="input-premium text-center text-xl font-semibold"
                          />
                        </div>
                        <span className="text-2xl font-bold text-gray-300 pt-5">:</span>
                        <div className="flex-1">
                          <label className="block text-xs text-gray-500 mb-1.5">Minutes</label>
                          <input
                            type="number"
                            min="0"
                            max="59"
                            value={customMinutes}
                            onChange={(e) => setCustomMinutes(Math.min(59, Math.max(0, parseInt(e.target.value) || 0)))}
                            className="input-premium text-center text-xl font-semibold"
                          />
                        </div>
                      </div>
                      <p className="text-sm text-gray-500 mt-4">
                        Scraper will run every{' '}
                        <strong className="text-ai-primary">
                          {customHours > 0 ? `${customHours}h ` : ''}{customMinutes > 0 ? `${customMinutes}m` : ''}
                          {customHours === 0 && customMinutes === 0 && '0m'}
                        </strong>
                      </p>
                    </div>
                  )}
                </AnimatedCard>
              )}
            </motion.div>
          )}

          {activeTab === 'scraper' && (
            <motion.div
              key="scraper"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* Manual Scraper */}
              <AnimatedCard className="p-8">
                <div className="flex items-center gap-5 mb-8">
                  <motion.div
                    animate={{ rotate: [0, 5, -5, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="w-16 h-16 bg-gradient-to-br from-orange-400 to-amber-500 rounded-2xl flex items-center justify-center shadow-lg"
                  >
                    <HiLightningBolt className="w-8 h-8 text-white" />
                  </motion.div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Run Scraper Now</h3>
                    <p className="text-gray-500">
                      Manually trigger the scraper to fetch latest articles
                    </p>
                  </div>
                </div>

                <GlowButton
                  onClick={handleRunNow}
                  disabled={startScraper.isPending}
                  loading={startScraper.isPending}
                  size="lg"
                  icon={<HiRefresh className="w-6 h-6" />}
                  className="!bg-gradient-to-r !from-orange-500 !to-amber-500"
                >
                  {startScraper.isPending ? 'Running...' : 'Start Scraping'}
                </GlowButton>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="mt-6 p-4 bg-amber-50 rounded-xl border border-amber-200"
                >
                  <p className="text-sm text-amber-800">
                    <strong>Note:</strong> This will scrape all enabled sources immediately.
                    The process runs in the background.
                  </p>
                </motion.div>
              </AnimatedCard>
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* Scraping Sessions */}
              <AnimatedCard className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Scraping Sessions</h3>
                  {scrapingSessions?.sessions && scrapingSessions.sessions.length > 0 && (
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleDeleteAll}
                      disabled={deleteAllHistory.isPending}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl text-sm font-medium transition-all border border-red-200 disabled:opacity-50"
                    >
                      <HiTrash className="w-4 h-4" />
                      Delete All
                    </motion.button>
                  )}
                </div>

                {sessionsLoading ? (
                  <div className="flex flex-col items-center justify-center py-16">
                    <AILoader variant="neural" size="lg" text="Loading sessions..." />
                  </div>
                ) : scrapingSessions?.sessions && scrapingSessions.sessions.length > 0 ? (
                  <div className="space-y-3">
                    {scrapingSessions.sessions.map((session: any, index: number) => (
                      <motion.div
                        key={session.job_id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`
                          flex items-center justify-between p-4 rounded-xl border-2 transition-all
                          ${session.is_latest
                            ? 'bg-gradient-to-r from-ai-primary/5 to-ai-secondary/5 border-ai-primary/30'
                            : 'bg-gray-50 border-gray-100 hover:border-gray-200'
                          }
                        `}
                      >
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${session.is_latest ? 'bg-ai-primary/20' : 'bg-green-100'}`}>
                            <HiCheckCircle className={`w-5 h-5 ${session.is_latest ? 'text-ai-primary' : 'text-green-600'}`} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-gray-900">
                                {session.completed_at || 'Unknown date'}
                              </p>
                              {session.is_latest && (
                                <span className="px-2 py-0.5 text-xs font-semibold bg-gradient-to-r from-ai-primary to-ai-secondary text-white rounded-full">
                                  Latest
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-500">
                              <strong className="text-ai-primary">{session.article_count}</strong> articles scraped
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <GlowButton
                            onClick={() => navigate(`/articles?job_id=${session.job_id}`)}
                            variant="secondary"
                            size="sm"
                            icon={<HiArrowRight className="w-4 h-4" />}
                          >
                            View
                          </GlowButton>
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => handleDeleteSession(session.job_id)}
                            disabled={deleteSession.isPending}
                            className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all disabled:opacity-50"
                            title="Delete session"
                          >
                            <HiTrash className="w-5 h-5" />
                          </motion.button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <motion.div
                      initial={{ scale: 0.8 }}
                      animate={{ scale: 1 }}
                      className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4"
                    >
                      <HiClock className="w-8 h-8 text-gray-400" />
                    </motion.div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">No sessions yet</h3>
                    <p className="text-gray-500 mb-6">Run the scraper to build history</p>
                    <GlowButton
                      onClick={() => setActiveTab('scraper')}
                      icon={<HiLightningBolt className="w-5 h-5" />}
                    >
                      Go to Run Now
                    </GlowButton>
                  </div>
                )}

                {scrapingSessions?.total > 0 && (
                  <p className="text-sm text-gray-500 mt-6 text-center">
                    Showing {scrapingSessions.sessions.length} of {scrapingSessions.total} sessions
                  </p>
                )}
              </AnimatedCard>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Delete Session Modal */}
      <AnimatePresence>
        {sessionToDelete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <HiExclamation className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Delete Session?</h3>
              </div>
              <p className="text-gray-600 mb-6">
                This will permanently delete this scraping session and all its articles.
                This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setSessionToDelete(null)}
                  className="btn-premium"
                >
                  Cancel
                </button>
                <GlowButton
                  onClick={confirmDeleteSession}
                  disabled={deleteSession.isPending}
                  loading={deleteSession.isPending}
                  className="!bg-red-500 hover:!bg-red-600"
                >
                  Delete
                </GlowButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete All Modal */}
      <AnimatePresence>
        {showDeleteAllConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <HiExclamation className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Delete All History?</h3>
              </div>
              <p className="text-gray-600 mb-3">
                This will permanently delete:
              </p>
              <ul className="space-y-2 mb-4">
                <li className="flex items-center gap-2 text-gray-600">
                  <HiTrash className="w-4 h-4 text-red-500" />
                  All scraping sessions ({scrapingSessions?.total || 0})
                </li>
                <li className="flex items-center gap-2 text-gray-600">
                  <HiTrash className="w-4 h-4 text-red-500" />
                  All scraped articles ({stats?.total_articles || 0})
                </li>
              </ul>
              <div className="p-3 bg-red-50 rounded-xl mb-6">
                <p className="text-sm text-red-700 font-medium">
                  This action cannot be undone!
                </p>
              </div>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowDeleteAllConfirm(false)}
                  className="btn-premium"
                >
                  Cancel
                </button>
                <GlowButton
                  onClick={confirmDeleteAll}
                  disabled={deleteAllHistory.isPending}
                  loading={deleteAllHistory.isPending}
                  className="!bg-red-500 hover:!bg-red-600"
                >
                  Delete Everything
                </GlowButton>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
