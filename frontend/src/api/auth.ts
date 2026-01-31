import api from './axios';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  UsageStats,
  RecentScrapingJob,
  AdminUserStats,
  AdminSetTokensRequest,
  AdminSetEnhancementsRequest,
  AdminAssignResponse,
  AdminToggleResponse,
  AdminDeleteResponse,
  AdminSetTierRequest
} from '../types/auth';

export const authApi = {
  // Login user
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    // Backend expects x-www-form-urlencoded, use URLSearchParams
    const params = new URLSearchParams();
    params.append('username', data.username);
    params.append('password', data.password);

    const response = await api.post<AuthResponse>('/api/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // Register new user
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  },

  // Get current user info
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },

  // Refresh access token (if endpoint exists)
  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  // Get usage statistics for current user
  getUsageStats: async (): Promise<UsageStats> => {
    const response = await api.get<UsageStats>('/api/auth/usage-stats');
    return response.data;
  },

  // Get recent scraping sessions for current user
  getScrapingHistory: async (limit: number = 10): Promise<RecentScrapingJob[]> => {
    const response = await api.get<RecentScrapingJob[]>(`/api/auth/scraping-history?limit=${limit}`);
    return response.data;
  },

  // Admin: Get all users' stats
  getAdminUsersStats: async (): Promise<AdminUserStats[]> => {
    const response = await api.get<AdminUserStats[]>('/api/auth/admin/users-stats');
    return response.data;
  },

  // Admin: Set user tokens
  adminSetTokens: async (data: AdminSetTokensRequest): Promise<AdminAssignResponse> => {
    const response = await api.post<AdminAssignResponse>('/api/auth/admin/set-tokens', data);
    return response.data;
  },

  // Admin: Set user enhancement limit
  adminSetEnhancements: async (data: AdminSetEnhancementsRequest): Promise<AdminAssignResponse> => {
    const response = await api.post<AdminAssignResponse>('/api/auth/admin/set-enhancements', data);
    return response.data;
  },

  // Admin: Trigger auto-assign tokens
  adminAutoAssignTokens: async (userId: number): Promise<AdminAssignResponse> => {
    const response = await api.post<AdminAssignResponse>(`/api/auth/admin/auto-assign-tokens/${userId}`);
    return response.data;
  },

  // Admin: Toggle user active status
  adminToggleUserActive: async (userId: number): Promise<AdminToggleResponse> => {
    const response = await api.post<AdminToggleResponse>(`/api/auth/admin/users/${userId}/toggle-active`);
    return response.data;
  },

  // Admin: Delete user
  adminDeleteUser: async (userId: number): Promise<AdminDeleteResponse> => {
    const response = await api.delete<AdminDeleteResponse>(`/api/auth/admin/users/${userId}`);
    return response.data;
  },

  // Admin: Toggle user admin status
  adminToggleUserAdmin: async (userId: number): Promise<AdminToggleResponse> => {
    const response = await api.post<AdminToggleResponse>(`/api/auth/admin/users/${userId}/toggle-admin`);
    return response.data;
  },

  // Admin: Set user subscription tier
  adminSetUserTier: async (userId: number, data: AdminSetTierRequest): Promise<AdminAssignResponse> => {
    const response = await api.post<AdminAssignResponse>(`/api/auth/admin/users/${userId}/set-tier`, data);
    return response.data;
  },

  // Admin: Reset user's monthly usage counts
  adminResetMonthlyUsage: async (userId: number): Promise<AdminAssignResponse> => {
    const response = await api.post<AdminAssignResponse>(`/api/auth/admin/users/${userId}/reset-monthly`);
    return response.data;
  },
};
