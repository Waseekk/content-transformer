/**
 * Layout Component - Premium app layout with animated navigation
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../../store/useAppStore';
import { CursorGlow } from '../ui';
import { OperationStatusBar } from './OperationStatusBar';
import { HiHome, HiNewspaper, HiSparkles, HiClock, HiLogout, HiChartBar, HiQuestionMarkCircle } from 'react-icons/hi';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { selectedArticle } = useAppStore();

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
    {
      path: '/support',
      label: 'Support',
      icon: <HiQuestionMarkCircle className="w-5 h-5" />,
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
        <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo - PNG with Typewriter + Cursor Effect */}
            <Link to="/" className="flex items-center gap-3 group py-2">
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300 }}
                className="flex items-center gap-1"
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
                    className="h-24 w-auto object-contain"
                  />
                </motion.div>
                {/* Blinking Cursor - 80% of logo height */}
                <motion.span
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                  className="w-1 h-16 bg-indigo-600 ml-1 rounded-sm"
                />
              </motion.div>

              {/* Tagline */}
              <div className="flex flex-col ml-2">
                <span className="text-sm font-semibold tagline-shimmer">AI powered clean and credible news</span>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-3">
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

            {/* Right Side: Logout */}
            <div className="flex items-center gap-4">
              {/* Logout */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleLogout}
                className="px-4 py-2 text-gray-600 hover:text-red-500 hover:bg-red-50 rounded-xl font-medium transition-all flex items-center gap-2"
              >
                <HiLogout className="w-5 h-5" />
                <span className="hidden sm:inline">Logout</span>
              </motion.button>
            </div>
          </div>
        </div>

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
            <div className="flex items-center gap-2">
              <img src="/swiftor-logo.png" alt="Swiftor" className="h-6 rounded" />
              <span className="text-sm font-medium text-gray-700">Swiftor</span>
            </div>
            <p className="text-sm font-medium tagline-shimmer ml-16">
              AI powered clean and credible news
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
