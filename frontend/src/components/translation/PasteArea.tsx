/**
 * Paste Area Component - Text input for article content
 */

import React, { useState } from 'react';
import { HiClipboard, HiTrash } from 'react-icons/hi';

interface PasteAreaProps {
  value: string;
  onChange: (value: string) => void;
  onTranslate: () => void;
  isLoading: boolean;
}

export const PasteArea: React.FC<PasteAreaProps> = ({
  value,
  onChange,
  onTranslate,
  isLoading,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(text);
    } catch {
      // Failed to read clipboard - browser may have blocked access
    }
  };

  const handleClear = () => {
    onChange('');
  };

  const charCount = value.length;
  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Paste Article Content
        </h3>

        <div className="flex gap-2">
          <button
            onClick={handlePaste}
            className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <HiClipboard className="w-4 h-4" />
            Paste from Clipboard
          </button>

          {value && (
            <button
              onClick={handleClear}
              className="px-3 py-2 text-sm bg-red-50 hover:bg-red-100 text-red-600 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <HiTrash className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Textarea */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder="Paste the full article content here... You can paste entire webpage HTML or just the article text."
        className={`
          w-full h-64 px-4 py-3 border-2 rounded-lg resize-y
          focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
          transition-all font-mono text-sm
          ${isFocused ? 'border-teal-400 bg-teal-50/30' : 'border-gray-300 bg-gray-50'}
        `}
      />

      {/* Footer */}
      <div className="flex items-center justify-between mt-4">
        {/* Stats */}
        <div className="flex gap-4 text-sm text-gray-600">
          <span>{charCount.toLocaleString()} characters</span>
          <span>•</span>
          <span>{wordCount.toLocaleString()} words</span>
        </div>

        {/* Process Button */}
        <button
          onClick={onTranslate}
          disabled={!value.trim() || isLoading}
          className={`
            px-6 py-3 rounded-lg font-semibold transition-all
            ${
              !value.trim() || isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-teal-500 text-white hover:bg-teal-600 hover:shadow-lg transform hover:scale-105'
            }
          `}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Processing...
            </span>
          ) : (
            '⚡ Process Content'
          )}
        </button>
      </div>
    </div>
  );
};
