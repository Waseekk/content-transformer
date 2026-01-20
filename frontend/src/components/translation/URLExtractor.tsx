/**
 * URL Extractor Component - Extract article content from URLs and translate
 * Uses Playwright → Trafilatura → Newspaper3k cascade + OpenAI translation
 */

import { useState } from 'react';
import type { KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { HiLink, HiSparkles, HiCheckCircle, HiRefresh } from 'react-icons/hi';
import { AnimatedCard, GlowButton } from '../ui';
import { useURLExtractAndTranslate } from '../../hooks/useURLExtraction';

interface URLExtractorProps {
  onExtractedAndTranslated: (englishContent: string, bengaliContent: string, title?: string, extractionMethod?: string) => void;
}

export const URLExtractor: React.FC<URLExtractorProps> = ({ onExtractedAndTranslated }) => {
  const [url, setUrl] = useState('');
  const [extractedUrl, setExtractedUrl] = useState<string | null>(null);
  const [wasBengaliPassthrough, setWasBengaliPassthrough] = useState(false);
  const extraction = useURLExtractAndTranslate();

  const normalizeUrl = (input: string): string => {
    let normalized = input.trim();
    if (!normalized) return '';

    // Auto-add https:// if missing protocol
    if (!normalized.startsWith('http://') && !normalized.startsWith('https://')) {
      normalized = 'https://' + normalized;
    }

    return normalized;
  };

  const isValidUrl = (input: string): boolean => {
    if (!input.trim()) return false;

    const normalized = normalizeUrl(input);
    try {
      const urlObj = new URL(normalized);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleExtractAndTranslate = async () => {
    if (!isValidUrl(url)) return;

    const normalizedUrl = normalizeUrl(url);

    try {
      const result = await extraction.mutateAsync(normalizedUrl);

      if (result.success && result.english_content && result.bengali_content) {
        const isBengali = result.extraction_method?.includes('bengali_passthrough') || false;
        setWasBengaliPassthrough(isBengali);

        onExtractedAndTranslated(
          result.english_content,
          result.bengali_content,
          result.title || undefined,
          result.extraction_method || undefined
        );
        setExtractedUrl(normalizedUrl); // Save the URL that was extracted
        // Don't clear the URL input - keep it visible
      }
    } catch {
      // Error handling is done in the hook
    }
  };

  const handleNewExtraction = () => {
    setExtractedUrl(null);
    setWasBengaliPassthrough(false);
    setUrl('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && isValidUrl(url) && !extraction.isPending) {
      handleExtractAndTranslate();
    }
  };

  // Show success state if URL was extracted
  if (extractedUrl) {
    return (
      <AnimatedCard delay={0.15} className="mb-6 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className={`w-10 h-10 bg-gradient-to-br rounded-xl flex items-center justify-center shadow-lg ${
                wasBengaliPassthrough
                  ? 'from-amber-400 to-orange-500'
                  : 'from-emerald-400 to-teal-500'
              }`}
            >
              <HiCheckCircle className="w-5 h-5 text-white" />
            </motion.div>
            <div>
              <h3 className="font-semibold text-gray-900">
                {wasBengaliPassthrough ? 'Bengali Content Extracted' : 'Extracted & Translated'}
              </h3>
              <p className="text-sm text-gray-500 truncate max-w-md" title={extractedUrl}>
                {extractedUrl}
              </p>
            </div>
          </div>
          <GlowButton
            variant="secondary"
            size="sm"
            onClick={handleNewExtraction}
            icon={<HiRefresh className="w-4 h-4" />}
          >
            New URL
          </GlowButton>
        </div>
      </AnimatedCard>
    );
  }

  return (
    <AnimatedCard delay={0.15} className="mb-6 p-6">
      <div className="flex items-center gap-3 mb-4">
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-xl flex items-center justify-center shadow-lg"
        >
          <HiLink className="w-5 h-5 text-white" />
        </motion.div>
        <div>
          <h3 className="font-semibold text-gray-900">Extract & Translate from URL</h3>
          <p className="text-sm text-gray-500">
            Paste URL to extract and translate in one step
          </p>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="https://www.bbc.com/travel/article/..."
            disabled={extraction.isPending}
            className={`
              w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl
              text-gray-900 placeholder-gray-400
              focus:bg-white focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/20
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          />
          {/* URL validation indicator */}
          {url && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`absolute right-3 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full ${
                isValidUrl(url) ? 'bg-emerald-400' : 'bg-gray-300'
              }`}
            />
          )}
        </div>
        <GlowButton
          onClick={handleExtractAndTranslate}
          disabled={!isValidUrl(url)}
          loading={extraction.isPending}
          icon={<HiSparkles className="w-5 h-5" />}
        >
          {extraction.isPending ? 'Processing...' : 'Extract & Translate'}
        </GlowButton>
      </div>

      <p className="mt-3 text-xs text-gray-400">
        Supports: English & Bengali news sites, blogs, travel articles
      </p>
    </AnimatedCard>
  );
};
