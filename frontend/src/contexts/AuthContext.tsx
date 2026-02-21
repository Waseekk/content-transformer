import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User, AuthContextType, RegisterRequest, UserClientConfig } from '../types/auth';
import { authApi } from '../api/auth';
import { userConfigApi } from '../api/admin';
import { useAppStore } from '../store/useAppStore';
import toast from 'react-hot-toast';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userConfig, setUserConfig] = useState<UserClientConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      refreshUser();
    } else {
      setIsLoading(false);
    }
  }, []);

  // Refresh user config (client, formats, UI settings)
  const refreshUserConfig = async () => {
    try {
      const config = await userConfigApi.getConfig();
      setUserConfig(config);
    } catch (error) {
      // Config fetch failed - use defaults
      setUserConfig(null);
    }
  };

  // Refresh user data from API
  const refreshUser = async () => {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
      // Also fetch user config
      await refreshUserConfig();
    } catch (error) {
      // Token is invalid or expired
      localStorage.removeItem('access_token');
      setUser(null);
      setUserConfig(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ username: email, password });

      // Store token
      localStorage.setItem('access_token', response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }

      // Set user
      setUser(response.user);

      // Fetch user config (client, formats, UI settings)
      await refreshUserConfig();

      // Reset app state on login (filters, pagination, etc.)
      useAppStore.getState().resetFilters();
      useAppStore.getState().clearTranslationState();
      useAppStore.getState().clearEnhancementState();

      toast.success('Login successful!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
      throw error;
    }
  };

  // Register function
  const register = async (data: RegisterRequest) => {
    try {
      const response = await authApi.register(data);

      // Store token
      localStorage.setItem('access_token', response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }

      // Set user
      setUser(response.user);

      // Fetch user config
      await refreshUserConfig();

      toast.success('Registration successful!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setUserConfig(null);
    toast.success('Logged out successfully');
  };

  const value: AuthContextType = {
    user,
    userConfig,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
    refreshUserConfig,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
