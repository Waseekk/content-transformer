/**
 * User Dashboard Page - Premium AI-themed usage statistics and history
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { authApi } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { AILoader } from '../components/ui';
import {
  HiTranslate,
  HiNewspaper,
  HiDocumentText,
  HiDatabase,
  HiClock,
  HiChartBar,
  HiUsers,
  HiRefresh,
  HiExternalLink,
  HiSparkles,
  HiTrendingUp,
  HiLightningBolt,
} from 'react-icons/hi';

export const UserDashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [showAdminStats, setShowAdminStats] = useState(false);

  // Fetch user stats
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery({
    queryKey: ['usageStats'],
    queryFn: authApi.getUsageStats,
  });

  // Fetch scraping history
  const { data: scrapingHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['scrapingHistory'],
    queryFn: () => authApi.getScrapingHistory(5),
  });

  // Fetch admin stats (only if admin)
  const { data: adminStats, isLoading: adminLoading } = useQuery({
    queryKey: ['adminUsersStats'],
    queryFn: authApi.getAdminUsersStats,
    enabled: user?.is_admin && showAdminStats,
  });

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-100 text-emerald-700 border border-emerald-200';
      case 'running':
        return 'bg-blue-100 text-blue-700 border border-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-700 border border-red-200';
      default:
        return 'bg-gray-100 text-gray-700 border border-gray-200';
    }
  };

  // Calculate token usage percentage
  const tokenPercentage = user
    ? Math.round((user.tokens_used / user.monthly_token_limit) * 100)
    : 0;

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  const cardHover = {
    scale: 1.02,
    transition: { duration: 0.2 }
  };

  return (
    <div className="min-h-screen">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-indigo-50/30 to-purple-50/40" />
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-indigo-200/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-radial from-purple-200/20 to-transparent rounded-full blur-3xl" />
      </div>

      <motion.div
        className="max-w-7xl mx-auto px-4 py-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Hero Header */}
        <motion.div variants={itemVariants} className="mb-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-5">
              <motion.div
                whileHover={{ scale: 1.05, rotate: 5 }}
                className="relative"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-xl">
                  <HiChartBar className="w-8 h-8 text-white" />
                </div>
                <motion.div
                  animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl blur-xl opacity-40"
                />
              </motion.div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-indigo-800 to-purple-800 bg-clip-text text-transparent">
                  My Statistics
                </h1>
                <p className="text-gray-500 mt-1 flex items-center gap-2">
                  <HiSparkles className="w-4 h-4 text-indigo-500" />
                  Track your AI-powered usage and activity
                </p>
              </div>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => refetchStats()}
              className="flex items-center gap-2 px-5 py-2.5 bg-white hover:bg-gray-50 rounded-xl text-gray-700 transition-all shadow-sm border border-gray-200"
            >
              <HiRefresh className="w-5 h-5" />
              Refresh
            </motion.button>
          </div>
        </motion.div>

        {/* Usage Limits Banner */}
        <motion.div variants={itemVariants} className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Translation Limit Card */}
          <motion.div
            whileHover={cardHover}
            className={`relative rounded-2xl p-6 text-white overflow-hidden shadow-xl ${
              stats?.translation_limit_exceeded
                ? 'bg-gradient-to-br from-orange-500 via-red-500 to-pink-600'
                : 'bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-700'
            }`}
          >
            {/* Decorative Elements */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full blur-xl" />

            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                    <HiTranslate className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-white/80 text-sm font-medium">Monthly Translations</p>
                    {stats?.translation_limit_exceeded && (
                      <span className="px-2 py-0.5 bg-white/20 rounded-full text-xs font-medium">
                        Limit Exceeded
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <p className="text-4xl font-bold mb-3">
                {stats?.translations_used_this_month || 0}
                <span className="text-xl font-normal opacity-70">
                  {' '}/ {stats?.monthly_translation_limit || 600}
                </span>
              </p>
              <div className="bg-white/20 rounded-full h-3 overflow-hidden backdrop-blur-sm">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(((stats?.translations_used_this_month || 0) / (stats?.monthly_translation_limit || 600)) * 100, 100)}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-full rounded-full ${
                    stats?.translation_limit_exceeded ? 'bg-red-200' : 'bg-white'
                  }`}
                />
              </div>
              <p className="text-sm opacity-80 mt-3 flex items-center gap-2">
                <HiLightningBolt className="w-4 h-4" />
                {stats?.translations_remaining || 0} translations remaining
              </p>
            </div>
          </motion.div>

          {/* Enhancement Limit Card */}
          <motion.div
            whileHover={cardHover}
            className={`relative rounded-2xl p-6 text-white overflow-hidden shadow-xl ${
              stats?.enhancement_limit_exceeded
                ? 'bg-gradient-to-br from-orange-500 via-red-500 to-pink-600'
                : 'bg-gradient-to-br from-teal-500 via-emerald-600 to-cyan-700'
            }`}
          >
            {/* Decorative Elements */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full blur-xl" />

            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                    <HiSparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-white/80 text-sm font-medium">Monthly Enhancements</p>
                    {stats?.enhancement_limit_exceeded && (
                      <span className="px-2 py-0.5 bg-white/20 rounded-full text-xs font-medium">
                        Limit Exceeded
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <p className="text-4xl font-bold mb-3">
                {stats?.enhancements_used_this_month || 0}
                <span className="text-xl font-normal opacity-70">
                  {' '}/ {stats?.monthly_enhancement_limit || 600}
                </span>
              </p>
              <div className="bg-white/20 rounded-full h-3 overflow-hidden backdrop-blur-sm">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(((stats?.enhancements_used_this_month || 0) / (stats?.monthly_enhancement_limit || 600)) * 100, 100)}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={`h-full rounded-full ${
                    stats?.enhancement_limit_exceeded ? 'bg-red-200' : 'bg-white'
                  }`}
                />
              </div>
              <p className="text-sm opacity-80 mt-3 flex items-center gap-2">
                <HiLightningBolt className="w-4 h-4" />
                {stats?.enhancements_remaining || 0} enhancements remaining
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* Token Usage Banner - ADMIN ONLY */}
        {user?.is_admin && (
          <motion.div
            variants={itemVariants}
            whileHover={cardHover}
            className="mb-8 relative bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-6 text-white overflow-hidden shadow-xl"
          >
            {/* Animated Glow */}
            <motion.div
              animate={{ opacity: [0.3, 0.6, 0.3], scale: [1, 1.1, 1] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/10 rounded-full blur-3xl"
            />

            <div className="relative flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <HiDatabase className="w-7 h-7" />
                </div>
                <div>
                  <p className="text-white/80 text-sm font-medium">Token Balance (Admin View)</p>
                  <p className="text-3xl font-bold mt-1">
                    {user?.tokens_remaining?.toLocaleString() || 0}
                    <span className="text-lg font-normal text-white/60">
                      {' '}/ {user?.monthly_token_limit?.toLocaleString() || 0}
                    </span>
                  </p>
                </div>
              </div>
              <div className="text-right bg-white/10 px-5 py-3 rounded-xl backdrop-blur-sm">
                <p className="text-white/80 text-sm">Used this month</p>
                <p className="text-2xl font-bold">
                  {user?.tokens_used?.toLocaleString() || 0}
                </p>
              </div>
            </div>
            <div className="relative bg-white/20 rounded-full h-3 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(tokenPercentage, 100)}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="bg-white h-full rounded-full"
              />
            </div>
            <p className="relative text-white/80 text-sm mt-3">
              {tokenPercentage}% of monthly limit used
            </p>
          </motion.div>
        )}

        {/* Usage Stats Grid */}
        {statsLoading ? (
          <div className="flex justify-center py-16">
            <AILoader variant="neural" size="lg" text="Loading your statistics..." />
          </div>
        ) : (
          <motion.div
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            {/* Total Translations */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="relative bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-6 text-white shadow-xl overflow-hidden"
            >
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl" />
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 backdrop-blur-sm">
                  <HiTranslate className="w-6 h-6" />
                </div>
                <motion.p
                  className="text-4xl font-bold mb-1"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200 }}
                >
                  {stats?.total_translations || 0}
                </motion.p>
                <p className="text-blue-100 text-sm">Total Translations</p>
              </div>
            </motion.div>

            {/* Hard News Count */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="relative bg-gradient-to-br from-slate-600 to-gray-800 rounded-2xl p-6 text-white shadow-xl overflow-hidden"
            >
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl" />
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 backdrop-blur-sm">
                  <HiNewspaper className="w-6 h-6" />
                </div>
                <motion.p
                  className="text-4xl font-bold mb-1"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                >
                  {stats?.hard_news_count || 0}
                </motion.p>
                <p className="text-gray-200 text-sm">Hard News Generated</p>
              </div>
            </motion.div>

            {/* Soft News Count */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="relative bg-gradient-to-br from-teal-500 to-emerald-600 rounded-2xl p-6 text-white shadow-xl overflow-hidden"
            >
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl" />
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 backdrop-blur-sm">
                  <HiDocumentText className="w-6 h-6" />
                </div>
                <motion.p
                  className="text-4xl font-bold mb-1"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                >
                  {stats?.soft_news_count || 0}
                </motion.p>
                <p className="text-teal-100 text-sm">Soft News Generated</p>
              </div>
            </motion.div>

            {/* Articles Scraped */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="relative bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl overflow-hidden"
            >
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl" />
              <div className="relative">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 backdrop-blur-sm">
                  <HiDatabase className="w-6 h-6" />
                </div>
                <motion.p
                  className="text-4xl font-bold mb-1"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.3 }}
                >
                  {stats?.total_articles_scraped || 0}
                </motion.p>
                <p className="text-purple-100 text-sm">Articles Scraped</p>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Additional Stats Row */}
        {!statsLoading && (
          <motion.div
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          >
            {/* Total Enhancements */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/60 shadow-lg"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-orange-400 to-amber-500 rounded-xl flex items-center justify-center shadow-lg">
                  <HiChartBar className="w-7 h-7 text-white" />
                </div>
                <div>
                  <motion.p
                    className="text-3xl font-bold text-gray-900"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                  >
                    {stats?.total_enhancements || 0}
                  </motion.p>
                  <p className="text-gray-500 text-sm">Total Enhancements</p>
                </div>
              </div>
            </motion.div>

            {/* Scraping Sessions */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/60 shadow-lg"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
                  <HiClock className="w-7 h-7 text-white" />
                </div>
                <div>
                  <motion.p
                    className="text-3xl font-bold text-gray-900"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                  >
                    {stats?.total_scraping_sessions || 0}
                  </motion.p>
                  <p className="text-gray-500 text-sm">Scraping Sessions</p>
                </div>
              </div>
            </motion.div>

            {/* Most Used Format */}
            <motion.div
              variants={itemVariants}
              whileHover={cardHover}
              className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/60 shadow-lg"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl flex items-center justify-center shadow-lg">
                  <HiTrendingUp className="w-7 h-7 text-white" />
                </div>
                <div>
                  <motion.p
                    className="text-3xl font-bold text-gray-900 capitalize"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                  >
                    {(() => {
                      const hard = stats?.hard_news_count || 0;
                      const soft = stats?.soft_news_count || 0;
                      if (hard === 0 && soft === 0) return '—';
                      return hard >= soft ? 'Hard News' : 'Soft News';
                    })()}
                  </motion.p>
                  <p className="text-gray-500 text-sm">Most Used Format</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Recent Scraping History */}
        <motion.div
          variants={itemVariants}
          className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200/60 shadow-lg mb-8 overflow-hidden"
        >
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <HiClock className="w-5 h-5 text-white" />
                </div>
                Recent Scraping Sessions
              </h2>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/articles')}
                className="text-sm text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-2 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-colors"
              >
                View All Articles
                <HiExternalLink className="w-4 h-4" />
              </motion.button>
            </div>
          </div>

          {historyLoading ? (
            <div className="p-8 flex justify-center">
              <AILoader variant="dots" size="md" text="Loading history..." />
            </div>
          ) : scrapingHistory && scrapingHistory.length > 0 ? (
            <div className="divide-y divide-gray-100">
              <AnimatePresence>
                {scrapingHistory.map((job, index) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ backgroundColor: 'rgba(249, 250, 251, 0.8)' }}
                    className="p-5 flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <motion.div
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md"
                      >
                        <HiDatabase className="w-6 h-6 text-white" />
                      </motion.div>
                      <div>
                        <p className="font-semibold text-gray-900">
                          Scraping Session #{job.id}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatDate(job.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold text-gray-900 text-lg">
                          {job.articles_count} articles
                        </p>
                        <span
                          className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(
                            job.status
                          )}`}
                        >
                          {job.status}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="p-12 text-center">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center"
              >
                <HiClock className="w-10 h-10 text-gray-400" />
              </motion.div>
              <p className="text-gray-500 font-medium">No scraping sessions yet</p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/articles')}
                className="mt-4 px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all"
              >
                Start Scraping
              </motion.button>
            </div>
          )}
        </motion.div>

        {/* Admin Section */}
        {user?.is_admin && (
          <motion.div
            variants={itemVariants}
            className="bg-white/80 backdrop-blur-sm rounded-2xl border-2 border-amber-200 shadow-lg overflow-hidden"
          >
            <div className="p-6 border-b border-amber-200 bg-gradient-to-r from-amber-50 to-yellow-50">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
                    <HiUsers className="w-5 h-5 text-white" />
                  </div>
                  Admin: All Users Statistics
                </h2>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowAdminStats(!showAdminStats)}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm ${
                    showAdminStats
                      ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg'
                      : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                  }`}
                >
                  {showAdminStats ? 'Hide Stats' : 'Show Stats'}
                </motion.button>
              </div>
            </div>

            <AnimatePresence>
              {showAdminStats && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="p-6">
                    {adminLoading ? (
                      <div className="flex justify-center py-12">
                        <AILoader variant="neural" size="md" text="Loading admin stats..." />
                      </div>
                    ) : adminStats && adminStats.length > 0 ? (
                      <div className="overflow-x-auto rounded-xl border border-gray-200">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                              <th className="text-left py-4 px-4 font-semibold text-gray-700">
                                User
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Role
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Tier
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Hard
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Soft
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Tokens
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Translations
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Enhance
                              </th>
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Status
                              </th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {adminStats.map((userStat, index) => (
                              <motion.tr
                                key={userStat.user_id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="hover:bg-gray-50/80 transition-colors"
                              >
                                <td className="py-4 px-4">
                                  <p className="font-medium text-gray-900">
                                    {userStat.full_name || 'No Name'}
                                  </p>
                                  <p className="text-xs text-gray-500 truncate max-w-[150px]">
                                    {userStat.email}
                                  </p>
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <span
                                    className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                                      userStat.is_admin
                                        ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white'
                                        : 'bg-blue-100 text-blue-700 border border-blue-200'
                                    }`}
                                  >
                                    {userStat.is_admin ? 'Admin' : 'User'}
                                  </span>
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <span
                                    className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                                      userStat.subscription_tier === 'premium'
                                        ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white'
                                        : userStat.subscription_tier === 'enterprise'
                                        ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white'
                                        : 'bg-gray-100 text-gray-700 border border-gray-200'
                                    }`}
                                  >
                                    {userStat.subscription_tier}
                                  </span>
                                </td>
                                <td className="py-4 px-3 text-center font-semibold text-gray-700">
                                  {userStat.hard_news_count}
                                </td>
                                <td className="py-4 px-3 text-center font-semibold text-teal-600">
                                  {userStat.soft_news_count}
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <div className="flex flex-col items-center">
                                    <span className="font-semibold text-indigo-600">
                                      {userStat.tokens_used_this_month.toLocaleString()}
                                    </span>
                                    <span className="text-xs text-gray-400">
                                      / {userStat.monthly_token_limit.toLocaleString()}
                                    </span>
                                  </div>
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <div className="flex flex-col items-center">
                                    <span className={`font-semibold ${
                                      userStat.translation_limit_exceeded
                                        ? 'text-red-600'
                                        : 'text-blue-600'
                                    }`}>
                                      {userStat.translations_used_this_month}
                                    </span>
                                    <span className="text-xs text-gray-400">
                                      / {userStat.monthly_translation_limit}
                                    </span>
                                  </div>
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <div className="flex flex-col items-center">
                                    <span className={`font-semibold ${
                                      userStat.enhancement_limit_exceeded
                                        ? 'text-red-600'
                                        : 'text-orange-600'
                                    }`}>
                                      {userStat.enhancements_used_this_month}
                                    </span>
                                    <span className="text-xs text-gray-400">
                                      / {userStat.monthly_enhancement_limit}
                                    </span>
                                  </div>
                                </td>
                                <td className="py-4 px-3 text-center">
                                  <span
                                    className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                                      userStat.is_active
                                        ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                                        : 'bg-red-100 text-red-700 border border-red-200'
                                    }`}
                                  >
                                    {userStat.is_active ? 'Active' : 'Inactive'}
                                  </span>
                                </td>
                              </motion.tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-12">
                        <HiUsers className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="font-medium">No users found</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};
