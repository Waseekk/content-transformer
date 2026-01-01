/**
 * Translation Result Component - Displays translation output
 */

import React, { useState } from 'react';
import { HiClipboard, HiClipboardCheck, HiDownload } from 'react-icons/hi';
import toast from 'react-hot-toast';

interface TranslationResultProps {
  original: string;
  translated: string;
  tokensUsed?: number;
  extractedData?: {
    headline?: string;
    content?: string;
    author?: string;
    published_date?: string;
  };
}

export const TranslationResult: React.FC<TranslationResultProps> = ({
  original,
  translated,
  tokensUsed,
  extractedData,
}) => {
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedTranslated, setCopiedTranslated] = useState(false);

  const handleCopy = async (text: string, type: 'original' | 'translated') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'original') {
        setCopiedOriginal(true);
        setTimeout(() => setCopiedOriginal(false), 2000);
      } else {
        setCopiedTranslated(true);
        setTimeout(() => setCopiedTranslated(false), 2000);
      }
      toast.success('Copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleDownload = (text: string, filename: string) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  return (
    <div className="space-y-6">
      {/* Token Usage Banner */}
      {tokensUsed && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-900">
              ⚡ Translation completed successfully
            </span>
            <span className="px-3 py-1 bg-blue-500 text-white text-sm font-semibold rounded-full">
              {tokensUsed.toLocaleString()} tokens used
            </span>
          </div>
        </div>
      )}

      {/* Extracted Data */}
      {extractedData && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📝 Extracted Article Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {extractedData.headline && (
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">Headline</p>
                <p className="text-sm text-gray-900 font-semibold">{extractedData.headline}</p>
              </div>
            )}
            {extractedData.author && (
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">Author</p>
                <p className="text-sm text-gray-900">{extractedData.author}</p>
              </div>
            )}
            {extractedData.published_date && (
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">Published Date</p>
                <p className="text-sm text-gray-900">{extractedData.published_date}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Side-by-Side Translation View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original Text */}
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
          <div className="bg-gray-100 px-6 py-3 border-b-2 border-gray-200 flex items-center justify-between">
            <h4 className="font-semibold text-gray-900">🔤 Original (English)</h4>
            <div className="flex gap-2">
              <button
                onClick={() => handleCopy(original, 'original')}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                title="Copy to clipboard"
              >
                {copiedOriginal ? (
                  <HiClipboardCheck className="w-4 h-4 text-green-600" />
                ) : (
                  <HiClipboard className="w-4 h-4 text-gray-600" />
                )}
              </button>
              <button
                onClick={() => handleDownload(original, 'original_article.txt')}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                title="Download"
              >
                <HiDownload className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto">
            <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
              {original}
            </p>
          </div>
        </div>

        {/* Translated Text */}
        <div className="bg-white rounded-xl border-2 border-teal-300 overflow-hidden shadow-lg">
          <div className="bg-gradient-to-r from-teal-500 to-blue-500 px-6 py-3 border-b-2 border-teal-300 flex items-center justify-between">
            <h4 className="font-semibold text-white">🇧🇩 Bengali Translation</h4>
            <div className="flex gap-2">
              <button
                onClick={() => handleCopy(translated, 'translated')}
                className="p-2 hover:bg-teal-600 rounded-lg transition-colors"
                title="Copy to clipboard"
              >
                {copiedTranslated ? (
                  <HiClipboardCheck className="w-4 h-4 text-white" />
                ) : (
                  <HiClipboard className="w-4 h-4 text-white" />
                )}
              </button>
              <button
                onClick={() => handleDownload(translated, 'bengali_translation.txt')}
                className="p-2 hover:bg-teal-600 rounded-lg transition-colors"
                title="Download"
              >
                <HiDownload className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto bg-teal-50/30">
            <p className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed font-bengali">
              {translated}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
