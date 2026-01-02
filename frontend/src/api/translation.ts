import axios from './axios';

export interface TranslationRequest {
  url?: string;
  text?: string;
}

export interface TranslationResponse {
  id: number;
  headline: string;
  content: string;
  original_url?: string;
  source_text?: string;
  tokens_used: number;
  created_at: string;
}

export interface TranslationListResponse {
  items: TranslationResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Extract and translate from URL
export const extractAndTranslate = async (url: string): Promise<TranslationResponse> => {
  const response = await axios.post('/api/translate/extract-and-translate', { url });
  return response.data;
};

// Translate text directly
export const translateText = async (text: string): Promise<TranslationResponse> => {
  const response = await axios.post('/api/translate/translate-text', { text });
  return response.data;
};

// Get translation history
export const getTranslations = async (
  page: number = 1,
  size: number = 10
): Promise<TranslationListResponse> => {
  const response = await axios.get('/api/translate/', {
    params: { skip: (page - 1) * size, limit: size },
  });
  return response.data;
};

// Get single translation
export const getTranslation = async (id: number): Promise<TranslationResponse> => {
  const response = await axios.get(`/api/translate/${id}`);
  return response.data;
};

// Delete translation
export const deleteTranslation = async (id: number): Promise<void> => {
  await axios.delete(`/api/translate/${id}`);
};
