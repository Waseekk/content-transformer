/**
 * Layout Component - Premium app layout with animated navigation
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../../store/useAppStore';
import { CursorGlow } from '../ui';
import { OperationStatusBar } from './OperationStatusBar';
import { HiHome, HiNewspaper, HiSparkles, HiClock, HiLogout, HiChartBar } from 'react-icons/hi';

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
            {/* Logo - Clean, Big, and Prominent */}
            <Link to="/" className="flex items-center gap-4 group py-2">
              {/* Logo Image with Subtle Glow */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300 }}
                className="relative"
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
                  className="h-12 w-12 rounded-xl object-cover"
                />
              </motion.div>

              {/* Brand Text - Large and Animated */}
              <div className="flex flex-col">
                {/* Swiftor Title - Swift(bold) + oval o + r(small) */}
                <motion.div className="flex items-baseline">
                  {/* Swift - BOLD with gradient animation */}
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="text-3xl font-extrabold tracking-tight logo-gradient-text"
                  >
                    Swift
                  </motion.span>
                  {/* Horizontal Oval O - with color animation */}
                  <motion.span
                    initial={{ opacity: 0, scaleX: 0 }}
                    animate={{ opacity: 1, scaleX: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                    className="inline-flex items-center justify-center ml-0.5"
                  >
                    <span
                      className="inline-block rounded-full logo-oval-border"
                      style={{
                        width: '2.2rem',
                        height: '0.85rem',
                        marginBottom: '2px',
                        borderWidth: '2px',
                        borderStyle: 'solid'
                      }}
                    />
                  </motion.span>
                  {/* r - with gradient animation */}
                  <motion.span
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                    className="text-xl font-normal logo-gradient-text"
                    style={{ marginLeft: '1px' }}
                  >
                    r
                  </motion.span>
                </motion.div>

                {/* Tagline */}
                <span className="text-sm font-semibold tagline-shimmer mt-0.5">AI powered clean and credible news</span>
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
            <p className="text-sm font-medium tagline-shimmer">
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
