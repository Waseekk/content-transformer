/**
 * Landing Page - Premium AI-themed navigation hub for Swiftor
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useScraperSites, useUpdateEnabledSites, useSetDefaultSites, useClearDefaultSites } from '../hooks/useScraper';
import { SwiftorLogo } from '../components/common';
import {
  HiCheck,
  HiStar,
  HiRefresh,
  HiExternalLink,
  HiChevronDown,
  HiNewspaper,
  HiSparkles,
  HiClock,
  HiChartBar,
  HiArrowRight,
  HiGlobeAlt
} from 'react-icons/hi';

interface NavCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  route: string;
  gradient: string;
  iconBg: string;
  delay: number;
  isAI?: boolean;
}

const NavCard = ({ icon, title, description, route, gradient, iconBg, delay, isAI }: NavCardProps) => (
  <Link to={route}>
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -8, transition: { duration: 0.2 } }}
      className={`
        relative overflow-hidden rounded-2xl p-6 h-full
        bg-white border border-gray-100
        shadow-premium hover:shadow-premium-lg
        transition-shadow duration-300
        group
      `}
    >
      {/* Gradient accent line at top */}
      <motion.div
        className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${gradient}`}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.5, delay: delay + 0.2 }}
      />

      {/* AI Glow effect for AI Assistant card */}
      {isAI && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-ai-primary/5 to-ai-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        />
      )}

      {/* Icon container */}
      <motion.div
        whileHover={{ scale: 1.1, rotate: [0, -5, 5, 0] }}
        transition={{ duration: 0.3 }}
        className={`
          w-14 h-14 rounded-xl ${iconBg}
          flex items-center justify-center mb-5
          ${isAI ? 'shadow-glow-sm' : ''}
        `}
      >
        {icon}
      </motion.div>

      {/* Content */}
      <h3 className={`text-xl font-bold mb-2 transition-colors ${isAI ? 'text-gradient' : 'text-gray-900 group-hover:text-gray-700'}`}>
        {title}
      </h3>
      <p className="text-gray-500 text-sm leading-relaxed mb-4">
        {description}
      </p>

      {/* Arrow indicator */}
      <div className={`flex items-center transition-colors ${isAI ? 'text-ai-primary' : 'text-gray-400 group-hover:text-teal-600'}`}>
        <span className="text-sm font-medium">Open</span>
        <motion.div
          className="ml-2"
          animate={{ x: [0, 4, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <HiArrowRight className="w-4 h-4" />
        </motion.div>
      </div>
    </motion.div>
  </Link>
);

const navigationCards: Omit<NavCardProps, 'delay'>[] = [
  {
    icon: <HiNewspaper className="w-7 h-7 text-blue-600" />,
    title: 'Articles',
    description: 'Browse and select news articles from your configured sources',
    route: '/articles',
    gradient: 'from-blue-500 to-blue-600',
    iconBg: 'bg-blue-50',
  },
  {
    icon: <HiSparkles className="w-7 h-7 text-ai-primary" />,
    title: 'AI Assistant',
    description: 'Generate Bengali news from any content with AI',
    route: '/translation',
    gradient: 'from-ai-primary to-ai-secondary',
    iconBg: 'bg-gradient-to-br from-ai-primary/20 to-ai-secondary/20',
    isAI: true,
  },
  {
    icon: <HiClock className="w-7 h-7 text-purple-600" />,
    title: 'Scheduler',
    description: 'Configure automated scraping schedules',
    route: '/scheduler',
    gradient: 'from-purple-500 to-purple-600',
    iconBg: 'bg-purple-50',
  },
  {
    icon: <HiChartBar className="w-7 h-7 text-orange-600" />,
    title: 'My Stats',
    description: 'View your usage analytics and translation history',
    route: '/my-dashboard',
    gradient: 'from-orange-500 to-orange-600',
    iconBg: 'bg-orange-50',
  },
];

export const DashboardPage = () => {
  const [showSources, setShowSources] = useState(false);
  const { data: sitesData } = useScraperSites();

  const updateSites = useUpdateEnabledSites();
  const setDefault = useSetDefaultSites();
  const clearDefault = useClearDefaultSites();

  const handleToggleSite = (siteName: string) => {
    if (!sitesData) return;
    const currentEnabled = sitesData.enabled_sites || [];
    const isCurrentlyEnabled = currentEnabled.includes(siteName);
    const newEnabled = isCurrentlyEnabled
      ? currentEnabled.filter((s: string) => s !== siteName)
      : [...currentEnabled, siteName];
    updateSites.mutate(newEnabled);
  };

  const enabledCount = sitesData?.enabled_sites?.length || 0;

  return (
    <div className="min-h-screen ai-gradient-bg">
      {/* Hero Section */}
      <div className="pt-12 pb-10">
        <div className="max-w-4xl mx-auto px-6">
          {/* Logo and Tagline - Centered with Step Reveal Animation */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="flex flex-col items-center"
          >
            <SwiftorLogo
              variant="stepReveal"
              size="xl"
              className="logo-dark mb-10 scale-[8] translate-x-16"
            />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
              className="text-xl tracking-widest uppercase ai-header-gradient ai-header-sparkle"
            >
              Your AI News Editor
            </motion.p>

          </motion.div>
        </div>
      </div>

      {/* Navigation Cards Grid */}
      <div className="max-w-4xl mx-auto px-6 pb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {navigationCards.map((card, index) => (
            <NavCard key={card.route} {...card} delay={0.1 + index * 0.1} />
          ))}
        </div>
      </div>

      {/* News Sources Section */}
      <div className="max-w-4xl mx-auto px-6 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => setShowSources(!showSources)}
            className={`
              w-full rounded-2xl p-5 text-left
              flex items-center justify-between
              transition-all duration-300
              ${showSources
                ? 'bg-white shadow-premium border border-gray-200'
                : 'bg-white/60 hover:bg-white border border-gray-100 hover:shadow-premium'
              }
            `}
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
                <HiGlobeAlt className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800">
                  News Sources
                </h3>
                <p className="text-sm text-gray-500">
                  {enabledCount} of {sitesData?.available_sites?.length || 0} sources enabled
                </p>
              </div>
            </div>
            <motion.div
              animate={{ rotate: showSources ? 180 : 0 }}
              transition={{ duration: 0.2 }}
              className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center"
            >
              <HiChevronDown className="w-5 h-5 text-gray-500" />
            </motion.div>
          </motion.button>

          {/* Expandable Sources List */}
          <AnimatePresence>
            {showSources && sitesData?.available_sites && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="mt-3 bg-white rounded-2xl p-6 border border-gray-100 shadow-premium">
                  <div className="flex items-center justify-between mb-5">
                    <p className="text-sm text-gray-500">
                      Click on a source to enable/disable it
                    </p>
                    <div className="flex items-center gap-2">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setDefault.mutate()}
                        disabled={setDefault.isPending || enabledCount === 0}
                        className={`
                          flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-all
                          ${sitesData.use_custom_default
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-gray-50 text-gray-600 hover:bg-amber-50 hover:text-amber-700 border border-gray-200'
                          }
                          disabled:opacity-50 disabled:cursor-not-allowed
                        `}
                      >
                        <HiStar className={`w-4 h-4 ${sitesData.use_custom_default ? 'text-amber-500' : ''}`} />
                        {sitesData.use_custom_default ? 'Default Set' : 'Set as Default'}
                      </motion.button>

                      {sitesData.use_custom_default && (
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => clearDefault.mutate()}
                          disabled={clearDefault.isPending}
                          className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200 transition-all disabled:opacity-50"
                        >
                          <HiRefresh className="w-4 h-4" />
                          Reset
                        </motion.button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {sitesData.available_sites.map((site: any, index: number) => {
                      const isEnabled = sitesData.enabled_sites?.includes(site.name);
                      return (
                        <motion.button
                          key={site.name}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.03 }}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleToggleSite(site.name)}
                          disabled={updateSites.isPending}
                          className={`
                            flex items-center justify-between p-4 rounded-xl border-2 transition-all text-left
                            ${isEnabled
                              ? 'border-ai-primary/30 bg-ai-primary/5 hover:bg-ai-primary/10'
                              : 'border-gray-200 bg-gray-50/50 hover:bg-gray-50 opacity-60'
                            }
                            disabled:cursor-wait
                          `}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3">
                              <motion.div
                                animate={isEnabled ? { scale: [1, 1.1, 1] } : {}}
                                transition={{ duration: 0.3 }}
                                className={`
                                  w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-colors
                                  ${isEnabled ? 'bg-ai-primary' : 'bg-gray-300'}
                                `}
                              >
                                {isEnabled && <HiCheck className="w-4 h-4 text-white" />}
                              </motion.div>
                              <p className={`font-medium truncate ${isEnabled ? 'text-gray-900' : 'text-gray-500'}`}>
                                {site.name.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                              </p>
                            </div>
                          </div>
                          <a
                            href={site.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="p-2 hover:bg-white rounded-lg transition-colors ml-2 flex-shrink-0"
                            title="Open in new tab"
                          >
                            <HiExternalLink className="w-4 h-4 text-gray-400 hover:text-ai-primary" />
                          </a>
                        </motion.button>
                      );
                    })}
                  </div>

                  {sitesData.use_custom_default && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="mt-4 text-xs text-amber-600 flex items-center gap-1"
                    >
                      <HiStar className="w-3 h-3" />
                      Custom default: {sitesData.default_sites?.length || 0} sites saved
                    </motion.p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
};
