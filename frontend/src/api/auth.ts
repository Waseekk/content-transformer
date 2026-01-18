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
  AdminAssignResponse
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
};
