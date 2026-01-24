/**
 * User Dashboard Page - Premium AI-themed usage statistics and history
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { authApi } from '../api/auth';
import { adminGetUserAllowedSites, adminSetUserAllowedSites } from '../api/scraper';
import type { AdminUserSitesResponse } from '../api/scraper';
import { useAuth } from '../contexts/AuthContext';
import { AILoader } from '../components/ui';
import type { AdminUserStats, AdminSetTierRequest } from '../types/auth';
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
  HiTrash,
  HiBan,
  HiCheckCircle,
  HiShieldCheck,
  HiShieldExclamation,
  HiX,
  HiGlobe,
} from 'react-icons/hi';

export const UserDashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showAdminStats, setShowAdminStats] = useState(false);
  const [deleteConfirmUser, setDeleteConfirmUser] = useState<AdminUserStats | null>(null);
  const [tierChangeUser, setTierChangeUser] = useState<AdminUserStats | null>(null);
  const [siteManageUser, setSiteManageUser] = useState<AdminUserStats | null>(null);
  const [userSitesData, setUserSitesData] = useState<AdminUserSitesResponse | null>(null);
  const [selectedAllowedSites, setSelectedAllowedSites] = useState<string[]>([]);

  // Admin mutations
  const toggleActiveMutation = useMutation({
    mutationFn: authApi.adminToggleUserActive,
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminUsersStats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to toggle user status');
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: authApi.adminDeleteUser,
    onSuccess: (data) => {
      toast.success(data.message);
      setDeleteConfirmUser(null);
      queryClient.invalidateQueries({ queryKey: ['adminUsersStats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete user');
    },
  });

  const toggleAdminMutation = useMutation({
    mutationFn: authApi.adminToggleUserAdmin,
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminUsersStats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to toggle admin status');
    },
  });

  const setTierMutation = useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: AdminSetTierRequest }) =>
      authApi.adminSetUserTier(userId, data),
    onSuccess: (data) => {
      toast.success(data.message);
      setTierChangeUser(null);
      queryClient.invalidateQueries({ queryKey: ['adminUsersStats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to change tier');
    },
  });

  // Fetch user's allowed sites when modal opens
  const fetchUserSitesMutation = useMutation({
    mutationFn: adminGetUserAllowedSites,
    onSuccess: (data) => {
      setUserSitesData(data);
      setSelectedAllowedSites(data.allowed_sites);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to fetch user sites');
      setSiteManageUser(null);
    },
  });

  // Update user's allowed sites
  const updateAllowedSitesMutation = useMutation({
    mutationFn: ({ userId, sites }: { userId: number; sites: string[] }) =>
      adminSetUserAllowedSites(userId, sites),
    onSuccess: (data) => {
      toast.success(data.message);
      setSiteManageUser(null);
      setUserSitesData(null);
      setSelectedAllowedSites([]);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update allowed sites');
    },
  });

  // Handle opening site management modal
  const handleOpenSiteManagement = (userStat: AdminUserStats) => {
    setSiteManageUser(userStat);
    fetchUserSitesMutation.mutate(userStat.user_id);
  };

  // Toggle site in selected list
  const toggleSiteSelection = (siteName: string) => {
    setSelectedAllowedSites(prev =>
      prev.includes(siteName)
        ? prev.filter(s => s !== siteName)
        : [...prev, siteName]
    );
  };

  // Select/Deselect all sites
  const toggleAllSites = () => {
    if (!userSitesData) return;
    if (selectedAllowedSites.length === userSitesData.all_available_sites.length) {
      setSelectedAllowedSites([]);
    } else {
      setSelectedAllowedSites([...userSitesData.all_available_sites]);
    }
  };

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
        className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8"
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
                              <th className="text-center py-4 px-3 font-semibold text-gray-700">
                                Actions
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
                                <td className="py-4 px-3">
                                  <div className="flex items-center justify-center gap-1">
                                    {/* Toggle Active/Inactive */}
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => toggleActiveMutation.mutate(userStat.user_id)}
                                      disabled={userStat.user_id === user?.id || toggleActiveMutation.isPending}
                                      className={`p-2 rounded-lg transition-colors ${
                                        userStat.user_id === user?.id
                                          ? 'opacity-30 cursor-not-allowed'
                                          : userStat.is_active
                                          ? 'text-orange-600 hover:bg-orange-50'
                                          : 'text-emerald-600 hover:bg-emerald-50'
                                      }`}
                                      title={userStat.is_active ? 'Deactivate user' : 'Activate user'}
                                    >
                                      {userStat.is_active ? (
                                        <HiBan className="w-5 h-5" />
                                      ) : (
                                        <HiCheckCircle className="w-5 h-5" />
                                      )}
                                    </motion.button>

                                    {/* Toggle Admin */}
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => toggleAdminMutation.mutate(userStat.user_id)}
                                      disabled={userStat.user_id === user?.id || toggleAdminMutation.isPending}
                                      className={`p-2 rounded-lg transition-colors ${
                                        userStat.user_id === user?.id
                                          ? 'opacity-30 cursor-not-allowed'
                                          : userStat.is_admin
                                          ? 'text-amber-600 hover:bg-amber-50'
                                          : 'text-gray-500 hover:bg-gray-100'
                                      }`}
                                      title={userStat.is_admin ? 'Revoke admin' : 'Grant admin'}
                                    >
                                      {userStat.is_admin ? (
                                        <HiShieldExclamation className="w-5 h-5" />
                                      ) : (
                                        <HiShieldCheck className="w-5 h-5" />
                                      )}
                                    </motion.button>

                                    {/* Change Tier */}
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => setTierChangeUser(userStat)}
                                      className="p-2 rounded-lg text-purple-600 hover:bg-purple-50 transition-colors"
                                      title="Change subscription tier"
                                    >
                                      <HiSparkles className="w-5 h-5" />
                                    </motion.button>

                                    {/* Manage Sites */}
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => handleOpenSiteManagement(userStat)}
                                      className="p-2 rounded-lg text-teal-600 hover:bg-teal-50 transition-colors"
                                      title="Manage allowed sites"
                                    >
                                      <HiGlobe className="w-5 h-5" />
                                    </motion.button>

                                    {/* Delete User */}
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => setDeleteConfirmUser(userStat)}
                                      disabled={userStat.user_id === user?.id}
                                      className={`p-2 rounded-lg transition-colors ${
                                        userStat.user_id === user?.id
                                          ? 'opacity-30 cursor-not-allowed'
                                          : 'text-red-600 hover:bg-red-50'
                                      }`}
                                      title="Delete user"
                                    >
                                      <HiTrash className="w-5 h-5" />
                                    </motion.button>
                                  </div>
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

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {deleteConfirmUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setDeleteConfirmUser(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
                  <HiTrash className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Delete User</h3>
                  <p className="text-sm text-gray-500">This action cannot be undone</p>
                </div>
              </div>
              <p className="text-gray-700 mb-6">
                Are you sure you want to delete <span className="font-semibold">{deleteConfirmUser.email}</span>?
                All their data including articles, translations, and enhancements will be permanently deleted.
              </p>
              <div className="flex gap-3 justify-end">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setDeleteConfirmUser(null)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => deleteUserMutation.mutate(deleteConfirmUser.user_id)}
                  disabled={deleteUserMutation.isPending}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
                >
                  {deleteUserMutation.isPending ? 'Deleting...' : 'Delete User'}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tier Change Modal */}
      <AnimatePresence>
        {tierChangeUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setTierChangeUser(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                    <HiSparkles className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">Change Subscription Tier</h3>
                    <p className="text-sm text-gray-500">{tierChangeUser.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => setTierChangeUser(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <HiX className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <p className="text-gray-700 mb-4">
                Current tier: <span className="font-semibold capitalize">{tierChangeUser.subscription_tier}</span>
              </p>
              <div className="space-y-3">
                {(['free', 'premium', 'enterprise'] as const).map((tier) => (
                  <motion.button
                    key={tier}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setTierMutation.mutate({ userId: tierChangeUser.user_id, data: { tier } })}
                    disabled={tier === tierChangeUser.subscription_tier || setTierMutation.isPending}
                    className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                      tier === tierChangeUser.subscription_tier
                        ? 'border-purple-500 bg-purple-50 cursor-not-allowed'
                        : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold capitalize text-gray-900">{tier}</p>
                        <p className="text-sm text-gray-500">
                          {tier === 'free' && 'Basic access with limited tokens'}
                          {tier === 'premium' && 'Extended limits and features'}
                          {tier === 'enterprise' && 'Unlimited access'}
                        </p>
                      </div>
                      {tier === tierChangeUser.subscription_tier && (
                        <span className="px-2 py-1 bg-purple-200 text-purple-700 rounded-lg text-xs font-medium">
                          Current
                        </span>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Site Management Modal */}
      <AnimatePresence>
        {siteManageUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => {
              setSiteManageUser(null);
              setUserSitesData(null);
              setSelectedAllowedSites([]);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-2xl w-full shadow-2xl max-h-[80vh] overflow-hidden flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center">
                    <HiGlobe className="w-6 h-6 text-teal-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">Manage Allowed Sites</h3>
                    <p className="text-sm text-gray-500">{siteManageUser.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSiteManageUser(null);
                    setUserSitesData(null);
                    setSelectedAllowedSites([]);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <HiX className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {fetchUserSitesMutation.isPending ? (
                <div className="flex justify-center py-12">
                  <AILoader variant="dots" size="md" text="Loading sites..." />
                </div>
              ) : userSitesData ? (
                <>
                  <div className="mb-4 p-3 bg-teal-50 border border-teal-200 rounded-xl">
                    <p className="text-sm text-teal-700">
                      <strong>Note:</strong> Select specific sites to restrict user access, or leave empty to allow access to all sites.
                    </p>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <p className="text-sm text-gray-600">
                      {selectedAllowedSites.length === 0 ? (
                        <span className="text-teal-600 font-medium">All sites allowed (no restrictions)</span>
                      ) : (
                        <span>{selectedAllowedSites.length} of {userSitesData.all_available_sites.length} sites selected</span>
                      )}
                    </p>
                    <button
                      onClick={toggleAllSites}
                      className="text-sm text-teal-600 hover:text-teal-700 font-medium"
                    >
                      {selectedAllowedSites.length === userSitesData.all_available_sites.length
                        ? 'Deselect All'
                        : 'Select All'}
                    </button>
                  </div>

                  <div className="flex-1 overflow-y-auto border border-gray-200 rounded-xl p-3 space-y-2 max-h-[300px]">
                    {userSitesData.all_available_sites.map((siteName) => (
                      <label
                        key={siteName}
                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                          selectedAllowedSites.includes(siteName)
                            ? 'bg-teal-50 border border-teal-200'
                            : 'bg-gray-50 border border-transparent hover:bg-gray-100'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedAllowedSites.includes(siteName)}
                          onChange={() => toggleSiteSelection(siteName)}
                          className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                        />
                        <span className="text-gray-700 font-medium">{siteName}</span>
                      </label>
                    ))}
                  </div>

                  <div className="flex gap-3 justify-end mt-6">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        setSiteManageUser(null);
                        setUserSitesData(null);
                        setSelectedAllowedSites([]);
                      }}
                      className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-xl font-medium transition-colors"
                    >
                      Cancel
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() =>
                        updateAllowedSitesMutation.mutate({
                          userId: siteManageUser.user_id,
                          sites: selectedAllowedSites,
                        })
                      }
                      disabled={updateAllowedSitesMutation.isPending}
                      className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
                    >
                      {updateAllowedSitesMutation.isPending ? 'Saving...' : 'Save Changes'}
                    </motion.button>
                  </div>
                </>
              ) : null}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
