export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  tokens_remaining: number;
  tokens_used: number;
  monthly_token_limit: number;
  subscription_tier: 'free' | 'premium' | 'enterprise';
  subscription_status: 'active' | 'paused' | 'cancelled';
  created_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// Usage Statistics Types
export interface UsageStats {
  total_translations: number;
  total_enhancements: number;
  hard_news_count: number;
  soft_news_count: number;
  other_formats_count: number;
  total_articles_scraped: number;
  total_scraping_sessions: number;
  // Translation limits
  translations_used_this_month: number;
  translations_remaining: number;
  monthly_translation_limit: number;
  translation_limit_exceeded: boolean;
  // Enhancement limits
  enhancements_used_this_month: number;
  enhancements_remaining: number;
  monthly_enhancement_limit: number;
  enhancement_limit_exceeded: boolean;
  // Tokens (hidden from regular users, kept for backward compatibility)
  tokens_used_this_month: number;
  tokens_remaining: number;
  most_used_format: string | null;
  average_tokens_per_translation: number;
}

export interface RecentScrapingJob {
  id: number;
  status: string;
  progress: number;
  articles_count: number;
  created_at: string;
  completed_at: string | null;
}

export interface AdminUserStats {
  user_id: number;
  email: string;
  full_name: string | null;
  subscription_tier: string;
  is_active: boolean;
  is_admin: boolean;
  total_translations: number;
  total_enhancements: number;
  hard_news_count: number;
  soft_news_count: number;
  total_articles_scraped: number;
  // Token info (admin only)
  tokens_used_this_month: number;
  tokens_remaining: number;
  monthly_token_limit: number;
  // Enhancement limits
  enhancements_used_this_month: number;
  enhancements_remaining: number;
  monthly_enhancement_limit: number;
  enhancement_limit_exceeded: boolean;
  // Translation limits
  translations_used_this_month: number;
  translations_remaining: number;
  monthly_translation_limit: number;
  translation_limit_exceeded: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AdminSetTokensRequest {
  user_id: number;
  new_limit: number;
  reset_used?: boolean;
}

export interface AdminSetEnhancementsRequest {
  user_id: number;
  new_limit: number;
  reset_used?: boolean;
}

export interface AdminAssignResponse {
  success: boolean;
  message: string;
  user_id: number;
  new_value: number;
}
