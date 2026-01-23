import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { Card, SwiftorLogo } from '../../components/common';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const oauthStatus = searchParams.get('oauth');

      if (oauthStatus === 'success') {
        try {
          // Exchange HTTP-only cookies for tokens
          const response = await axios.get(`${API_BASE_URL}/api/oauth/exchange-tokens`, {
            withCredentials: true, // Important: send cookies
          });

          const { access_token, refresh_token } = response.data;

          // Store tokens in localStorage (same as regular login)
          localStorage.setItem('access_token', access_token);
          if (refresh_token) {
            localStorage.setItem('refresh_token', refresh_token);
          }

          // Refresh user data
          await refreshUser();

          setStatus('success');
          toast.success('Google login successful!');

          // Redirect to dashboard after brief delay
          setTimeout(() => {
            navigate('/', { replace: true });
          }, 1000);
        } catch (error: any) {
          setStatus('error');
          setErrorMessage(
            error.response?.data?.detail || 'Failed to complete authentication. Please try again.'
          );
          toast.error('Authentication failed');
        }
      } else {
        // No OAuth status in URL or failed
        setStatus('error');
        setErrorMessage('Invalid OAuth callback. Please try logging in again.');
      }
    };

    handleOAuthCallback();
  }, [searchParams, navigate, refreshUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50/50 to-purple-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="flex flex-col items-center"
          >
            <SwiftorLogo
              variant="typewriter"
              size="xl"
              showTagline={false}
              className="logo-dark scale-[7] mb-14 translate-x-16"
            />
          </motion.div>
        </div>

        <Card>
          <div className="text-center py-8">
            {status === 'loading' && (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Completing authentication...</p>
              </>
            )}

            {status === 'success' && (
              <>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-6 h-6 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <p className="text-gray-600">Login successful! Redirecting...</p>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-6 h-6 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
                <p className="text-red-600 mb-4">{errorMessage}</p>
                <button
                  onClick={() => navigate('/login')}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Return to login
                </button>
              </>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
