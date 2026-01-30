/**
 * Layout Component - Premium app layout with animated navigation
 */

import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../../store/useAppStore';
import { CursorGlow } from '../ui';
import { OperationStatusBar } from './OperationStatusBar';
import { HiHome, HiNewspaper, HiSparkles, HiClock, HiLogout, HiChartBar, HiQuestionMarkCircle, HiMenu, HiX } from 'react-icons/hi';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { selectedArticle } = useAppStore();
  const [isUserPanelOpen, setIsUserPanelOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const navItems = [
    {
      path: '/',
      label: 'Dashboard',
      icon: <HiHome className="w-5 h-5" />,
    },
    {
      path: '/articles',
      label: 'Articles',
      icon: <HiNewspaper className="w-5 h-5" />,
    },
    {
      path: '/translation',
      label: 'AI Assistant',
      icon: <HiSparkles className="w-5 h-5" />,
      badge: selectedArticle ? '1' : null,
      highlight: true,
    },
    {
      path: '/scheduler',
      label: 'Scheduler',
      icon: <HiClock className="w-5 h-5" />,
    },
    {
      path: '/my-dashboard',
      label: 'My Stats',
      icon: <HiChartBar className="w-5 h-5" />,
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Cursor Glow Effect */}
      <CursorGlow />

      {/* Global Operation Status Bar */}
      <OperationStatusBar />

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-card border-b border-gray-200/50 sticky top-0 z-50"
      >
        <div className="w-full max-w-[98vw] lg:max-w-[96vw] 2xl:max-w-[94vw] mx-auto pl-0 pr-2 sm:pr-4">
          <div className="flex items-center justify-between h-20 relative">
            {/* Logo - PNG with Typewriter + Cursor Effect */}
            <Link to="/" className="flex items-center gap-0 group py-2 z-10">
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300 }}
                className="flex items-center gap-0"
              >
                {/* Logo with typewriter reveal effect */}
                <motion.div
                  className="relative"
                  style={{ clipPath: 'inset(0 100% 0 0)' }}
                  animate={{ clipPath: 'inset(0 0% 0 0)' }}
                  transition={{ duration: 1.2, ease: 'easeOut' }}
                >
                  <motion.img
                    animate={{
                      filter: [
                        'drop-shadow(0 0 8px rgba(99, 102, 241, 0.3))',
                        'drop-shadow(0 0 15px rgba(99, 102, 241, 0.5))',
                        'drop-shadow(0 0 8px rgba(99, 102, 241, 0.3))'
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    src="/swiftor-logo.png"
                    alt="Swiftor"
                    className="h-32 w-auto object-contain"
                  />
                </motion.div>
                {/* Blinking Cursor - 80% of logo height */}
                <motion.span
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                  className="w-0.5 h-[26px] bg-indigo-600 rounded-sm"
                />
              </motion.div>
            </Link>

            {/* Navigation - Absolutely Centered on Page */}
            <nav className="hidden md:flex items-center gap-2 absolute left-1/2 -translate-x-1/2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                const isAIAssistant = item.highlight;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className="relative"
                  >
                    <motion.div
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                      className={`
                        relative px-5 py-2.5 rounded-xl font-medium flex items-center gap-2 overflow-hidden
                        ${isActive
                          ? isAIAssistant
                            ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white nav-active-purple'
                            : 'bg-gray-950 text-white nav-active-dark'
                          : isAIAssistant
                            ? 'text-violet-600 hover:bg-violet-50 hover:text-violet-700'
                            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                        }
                      `}
                    >
                      {/* Inner animated glow */}
                      {isActive && (
                        <motion.div
                          className={`absolute inset-0 ${isAIAssistant ? 'nav-inner-glow-purple' : 'nav-inner-glow-dark'}`}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        />
                      )}
                      <span className={`relative z-10 ${isAIAssistant && !isActive ? 'text-violet-500' : ''}`}>
                        {item.icon}
                      </span>
                      <span className="relative z-10">{item.label}</span>
                      {item.badge && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center shadow-md z-20"
                        >
                          {item.badge}
                        </motion.span>
                      )}
                    </motion.div>
                  </Link>
                );
              })}
            </nav>

            {/* Right Side: User Menu */}
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsUserPanelOpen(true)}
                className="p-2.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all"
              >
                <HiMenu className="w-6 h-6" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* User Panel Overlay */}
        <AnimatePresence>
          {isUserPanelOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsUserPanelOpen(false)}
                className="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60]"
              />
              {/* Slide-out Panel */}
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                className="fixed right-0 top-0 h-full w-72 bg-white shadow-2xl z-[70] flex flex-col"
              >
                {/* Panel Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-100">
                  <span className="text-lg font-semibold text-gray-800">Menu</span>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setIsUserPanelOpen(false)}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all"
                  >
                    <HiX className="w-5 h-5" />
                  </motion.button>
                </div>

                {/* Panel Content */}
                <div className="flex-1 p-4 space-y-2">
                  <Link
                    to="/support"
                    onClick={() => setIsUserPanelOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      location.pathname === '/support'
                        ? 'bg-gray-900 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <HiQuestionMarkCircle className="w-5 h-5" />
                    <span className="font-medium">Support</span>
                  </Link>
                </div>

                {/* Panel Footer - Logout */}
                <div className="p-4 border-t border-gray-100">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl font-medium transition-all"
                  >
                    <HiLogout className="w-5 h-5" />
                    <span>Logout</span>
                  </motion.button>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-gray-200/50">
          <nav className="flex overflow-x-auto scrollbar-hide py-2 px-3 gap-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const isAIAssistant = item.highlight;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    relative flex flex-col items-center gap-1 px-4 py-2.5 rounded-xl min-w-[76px] flex-shrink-0 overflow-hidden
                    transition-all duration-300 ease-out
                    ${isActive
                      ? isAIAssistant
                        ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white nav-active-purple'
                        : 'bg-gray-950 text-white nav-active-dark'
                      : isAIAssistant
                        ? 'text-violet-600'
                        : 'text-gray-500 hover:bg-gray-50'
                    }
                  `}
                >
                  {/* Inner shimmer for active state */}
                  {isActive && (
                    <div className={`absolute inset-0 ${isAIAssistant ? 'nav-inner-glow-purple' : 'nav-inner-glow-dark'}`} />
                  )}
                  <span className="relative z-10">{item.icon}</span>
                  <span className="relative z-10 text-xs font-medium whitespace-nowrap">{item.label}</span>
                  {item.badge && (
                    <span className="absolute top-0 right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center z-20">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-4rem)]">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200/50 mt-12">
        <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm font-medium tagline-shimmer">
              AI Powered Clean and Credible News
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                &copy; {new Date().getFullYear()} Swiftor.
              </span>
              <span className="text-xs text-gray-400">
                A Product of Data Insightopia
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
