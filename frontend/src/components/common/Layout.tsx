/**
 * Layout Component - Premium app layout with animated navigation
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../../store/useAppStore';
import { CursorGlow } from '../ui';
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

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-card border-b border-gray-200/50 sticky top-0 z-50"
      >
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <motion.img
                whileHover={{ scale: 1.05 }}
                src="/swiftor-logo.jpeg"
                alt="Swiftor"
                className="h-10 rounded-lg"
              />
              <div className="flex flex-col">
                <span className="text-xl font-bold text-gray-800 group-hover:text-ai-primary transition-colors">
                  Swiftor
                </span>
                <span className="text-xs text-gray-500 -mt-1">AI News Editor</span>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className="relative"
                  >
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`
                        relative px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2
                        ${isActive
                          ? item.highlight
                            ? 'bg-gradient-to-r from-ai-primary to-ai-secondary text-white shadow-glow-sm'
                            : 'bg-gray-900 text-white'
                          : item.highlight
                            ? 'text-ai-primary hover:bg-ai-primary/10'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }
                      `}
                    >
                      {item.icon}
                      <span>{item.label}</span>
                      {item.badge && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center shadow-md"
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
          <nav className="flex overflow-x-auto scrollbar-hide py-2 px-2 gap-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    relative flex flex-col items-center gap-1 px-3 py-2 rounded-xl transition-all min-w-[72px] flex-shrink-0
                    ${isActive
                      ? item.highlight
                        ? 'bg-gradient-to-r from-ai-primary to-ai-secondary text-white'
                        : 'bg-gray-900 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                    }
                  `}
                >
                  {item.icon}
                  <span className="text-xs font-medium whitespace-nowrap">{item.label}</span>
                  {item.badge && (
                    <span className="absolute top-0 right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">
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
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <img src="/swiftor-logo.jpeg" alt="Swiftor" className="h-6 rounded" />
              <span className="text-sm font-medium text-gray-700">Swiftor</span>
            </div>
            <p className="text-gray-500 text-sm">
              AI-Powered News Translation & Generation Platform
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                &copy; {new Date().getFullYear()} Swiftor
              </span>
              <span className="w-1 h-1 rounded-full bg-gray-300"></span>
              <span className="text-xs text-gray-400">
                বাংলার কলম্বাস
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
