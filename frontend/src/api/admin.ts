/**
 * Admin API Client
 * API calls for admin format and client configuration management
 */

import api from './axios';

// ============================================================================
// TYPES
// ============================================================================

export interface FormatRules {
  max_sentences_per_paragraph?: number | null;
  quotation_on_last_line?: boolean;
  quotation_must_end_paragraph?: boolean;
  allow_subheads?: boolean;
  intro_max_sentences?: number | null;
  intro_paragraphs_before_subhead?: number | null;
  min_words?: number | null;
  max_words?: number | null;
  save_original_content?: boolean;
}

export interface FormatConfig {
  id: number;
  slug: string;
  display_name: string;
  description?: string;
  icon: string;
  system_prompt: string;
  temperature: number;
  max_tokens: number;
  rules: FormatRules;
  is_active: boolean;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface FormatConfigCreate {
  slug: string;
  display_name: string;
  description?: string;
  icon?: string;
  system_prompt: string;
  temperature?: number;
  max_tokens?: number;
  rules?: FormatRules;
  is_active?: boolean;
}

export interface FormatConfigUpdate {
  slug?: string;
  display_name?: string;
  description?: string;
  icon?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  rules?: FormatRules;
  is_active?: boolean;
}

export interface FormatListResponse {
  formats: FormatConfig[];
  total: number;
}

export interface UISettings {
  show_content_preview?: boolean;
  workflow_type?: 'full' | 'simple';
  show_format_selection?: boolean;
  app_title?: string;
  // NEW: Client UI customization settings
  hide_format_labels?: boolean;        // Hide "হার্ড নিউজ/সফট নিউজ" everywhere
  hide_main_content_export?: boolean;  // Hide English source in Word export
  download_prefix?: string;            // Custom prefix (empty = use client name)
}

export interface ClientConfig {
  id: number;
  name: string;
  slug: string;
  allowed_format_ids: number[];
  default_format_id?: number;
  ui_settings: UISettings;
  display_overrides: Record<string, string>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientConfigCreate {
  name: string;
  slug: string;
  allowed_format_ids?: number[];
  default_format_id?: number;
  ui_settings?: UISettings;
  display_overrides?: Record<string, string>;
  is_active?: boolean;
}

export interface ClientConfigUpdate {
  name?: string;
  slug?: string;
  allowed_format_ids?: number[];
  default_format_id?: number;
  ui_settings?: UISettings;
  display_overrides?: Record<string, string>;
  is_active?: boolean;
}

export interface ClientListResponse {
  clients: ClientConfig[];
  total: number;
}

export interface ClientUser {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface UserWithClient {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  client_config_id: number | null;
  client: {
    id: number;
    name: string;
    slug: string;
  } | null;
}

export interface UserAssignRequest {
  client_config_id: number | null;
}

// ============================================================================
// FORMAT CONFIG API
// ============================================================================

export const formatApi = {
  // List all formats
  list: async (includeInactive = false): Promise<FormatListResponse> => {
    const response = await api.get<FormatListResponse>(
      `/api/admin/formats?include_inactive=${includeInactive}`
    );
    return response.data;
  },

  // Get a single format
  get: async (id: number): Promise<FormatConfig> => {
    const response = await api.get<FormatConfig>(`/api/admin/formats/${id}`);
    return response.data;
  },

  // Create a new format
  create: async (data: FormatConfigCreate): Promise<FormatConfig> => {
    const response = await api.post<FormatConfig>('/api/admin/formats', data);
    return response.data;
  },

  // Update a format
  update: async (id: number, data: FormatConfigUpdate): Promise<FormatConfig> => {
    const response = await api.put<FormatConfig>(`/api/admin/formats/${id}`, data);
    return response.data;
  },

  // Delete a format (soft delete by default)
  delete: async (id: number, hardDelete = false): Promise<void> => {
    await api.delete(`/api/admin/formats/${id}?hard_delete=${hardDelete}`);
  },

  // Restore a soft-deleted format
  restore: async (id: number): Promise<FormatConfig> => {
    const response = await api.post<FormatConfig>(`/api/admin/formats/${id}/restore`);
    return response.data;
  },

  // Get clients using a format
  getClients: async (id: number): Promise<FormatClientsResponse> => {
    const response = await api.get<FormatClientsResponse>(`/api/admin/formats/${id}/clients`);
    return response.data;
  },
};

export interface FormatClientInfo {
  id: number;
  name: string;
  slug: string;
  is_default: boolean;
  display_override: string | null;
}

export interface FormatClientsResponse {
  format_id: number;
  format_name: string;
  clients: FormatClientInfo[];
  total: number;
}

// ============================================================================
// CLIENT CONFIG API
// ============================================================================

export const clientApi = {
  // List all clients
  list: async (includeInactive = false): Promise<ClientListResponse> => {
    const response = await api.get<ClientListResponse>(
      `/api/admin/clients?include_inactive=${includeInactive}`
    );
    return response.data;
  },

  // Get a single client
  get: async (id: number): Promise<ClientConfig> => {
    const response = await api.get<ClientConfig>(`/api/admin/clients/${id}`);
    return response.data;
  },

  // Create a new client
  create: async (data: ClientConfigCreate): Promise<ClientConfig> => {
    const response = await api.post<ClientConfig>('/api/admin/clients', data);
    return response.data;
  },

  // Update a client
  update: async (id: number, data: ClientConfigUpdate): Promise<ClientConfig> => {
    const response = await api.put<ClientConfig>(`/api/admin/clients/${id}`, data);
    return response.data;
  },

  // Delete a client (soft delete by default)
  delete: async (id: number, hardDelete = false): Promise<void> => {
    await api.delete(`/api/admin/clients/${id}?hard_delete=${hardDelete}`);
  },

  // List users assigned to a client
  listUsers: async (clientId: number): Promise<ClientUser[]> => {
    const response = await api.get<ClientUser[]>(`/api/admin/clients/${clientId}/users`);
    return response.data;
  },

  // Assign user to a client
  assignUser: async (userId: number, clientConfigId: number | null): Promise<void> => {
    await api.post(`/api/admin/clients/users/${userId}/assign`, {
      client_config_id: clientConfigId,
    });
  },

  // List all users with their client assignments
  listAllUsers: async (): Promise<UserWithClient[]> => {
    const response = await api.get<UserWithClient[]>('/api/admin/clients/users/all');
    return response.data;
  },
};

// ============================================================================
// USER CONFIG API (for current user)
// ============================================================================

export interface UserFormatConfig {
  id: number;
  slug: string;
  display_name: string;
  description?: string;
  icon: string;
}

export interface UserClientConfig {
  client: ClientConfig | null;
  formats: UserFormatConfig[];
  default_format: UserFormatConfig | null;
  ui_settings: UISettings;
  display_overrides: Record<string, string>;
}

export const userConfigApi = {
  // Get current user's config
  getConfig: async (): Promise<UserClientConfig> => {
    const response = await api.get<UserClientConfig>('/api/user/config');
    return response.data;
  },

  // Get current user's allowed formats
  getFormats: async (): Promise<UserFormatConfig[]> => {
    const response = await api.get<UserFormatConfig[]>('/api/user/formats');
    return response.data;
  },
};
