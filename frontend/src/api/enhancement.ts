import axios from './axios';

export interface EnhancementRequest {
  text: string;
  headline: string;
  formats: string[];
  article_info?: {
    source?: string;
    date?: string;
    author?: string;
  };
}

export interface FormatResult {
  content: string;
  tokens_used: number;
}

export interface EnhancementResponse {
  id: number;
  headline: string;
  original_text: string;
  formats: Record<string, FormatResult>;
  total_tokens_used: number;
  created_at: string;
}

export interface EnhancementListResponse {
  items: EnhancementResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface FormatInfo {
  name: string;
  description: string;
  icon: string;
  available: boolean;
  tier_required?: string;
}

// Get available formats
export const getAvailableFormats = async (): Promise<FormatInfo[]> => {
  const response = await axios.get('/api/enhance/formats');
  return response.data.formats;
};

// Enhance text to multiple formats
export const enhanceText = async (data: EnhancementRequest): Promise<EnhancementResponse> => {
  const response = await axios.post('/api/enhance/', data);
  return response.data;
};

// Get enhancement history
export const getEnhancements = async (
  page: number = 1,
  size: number = 10
): Promise<EnhancementListResponse> => {
  const response = await axios.get('/api/enhance/', {
    params: { skip: (page - 1) * size, limit: size },
  });
  return response.data;
};

// Get single enhancement
export const getEnhancement = async (id: number): Promise<EnhancementResponse> => {
  const response = await axios.get(`/api/enhance/${id}`);
  return response.data;
};

// Delete enhancement
export const deleteEnhancement = async (id: number): Promise<void> => {
  await axios.delete(`/api/enhance/${id}`);
};
