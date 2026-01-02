/**
 * Layout Component - Main app layout with navigation
 */

import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';
import { HiHome, HiNewspaper, HiTranslate, HiClock, HiLogout } from 'react-icons/hi';

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
      label: 'Translation',
      icon: <HiTranslate className="w-5 h-5" />,
      badge: selectedArticle ? '1' : null,
    },
    {
      path: '/scheduler',
      label: 'Scheduler',
      icon: <HiClock className="w-5 h-5" />,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">TN</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">
                  Travel News Translator
                </h1>
                <p className="text-xs text-gray-600">Content Workflow Platform</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      relative px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2
                      ${
                        isActive
                          ? 'bg-teal-500 text-white shadow-lg'
                          : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    {item.icon}
                    {item.label}
                    {item.badge && (
                      <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* Logout */}
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <HiLogout className="w-5 h-5" />
              Logout
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-gray-200">
          <nav className="flex justify-around py-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    relative flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all
                    ${
                      isActive
                        ? 'text-teal-500'
                        : 'text-gray-600'
                    }
                  `}
                >
                  {item.icon}
                  <span className="text-xs font-medium">{item.label}</span>
                  {item.badge && (
                    <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-4rem)]">{children}</main>

      {/* Footer */}
      <footer className="bg-white border-t-2 border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center text-gray-600 text-sm">
            <p>
              Travel News Translator &copy; {new Date().getFullYear()} - Built
              with React, FastAPI, and OpenAI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
