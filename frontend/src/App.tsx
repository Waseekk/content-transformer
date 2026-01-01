import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { queryClient } from './services/queryClient';
import { AuthProvider } from './contexts/AuthContext';

// Auth pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Main pages
import { DashboardPage } from './pages/DashboardPage';
import { ArticlesPage } from './pages/ArticlesPage';
import { TranslationPage } from './pages/TranslationPage';
import { SchedulerPage } from './pages/SchedulerPage';

// Layout
import { Layout } from './components/common/Layout';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes with Layout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/articles"
            element={
              <ProtectedRoute>
                <Layout>
                  <ArticlesPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/translation"
            element={
              <ProtectedRoute>
                <Layout>
                  <TranslationPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/scheduler"
            element={
              <ProtectedRoute>
                <Layout>
                  <SchedulerPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Redirect old routes */}
          <Route path="/dashboard" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </BrowserRouter>
      </AuthProvider>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
