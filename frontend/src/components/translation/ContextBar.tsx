/**
 * Context Bar - Shows selected article context in Translation page
 */

import React from 'react';
import type { Article } from '../../types';
import { HiX, HiExternalLink } from 'react-icons/hi';

interface ContextBarProps {
  article: Article;
  onClear: () => void;
}

export const ContextBar: React.FC<ContextBarProps> = ({ article, onClear }) => {
  return (
    <div className="bg-gradient-to-r from-teal-50 to-blue-50 rounded-xl p-6 border-2 border-teal-200 mb-6">
      <div className="flex items-start justify-between gap-4">
        {/* Left side - Article info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-3 py-1 bg-teal-500 text-white text-xs font-semibold rounded-full">
              SELECTED ARTICLE
            </span>
          </div>

          <h2 className="text-xl font-bold text-gray-900 mb-3 font-serif">
            {article.headline}
          </h2>

          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              📰 {article.publisher}
            </span>
            <span className="flex items-center gap-1">
              ⏰ {article.published_time || 'N/A'}
            </span>
            {article.country && (
              <span className="flex items-center gap-1">
                🌍 {article.country}
              </span>
            )}
          </div>

          {article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {article.tags.slice(0, 5).map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 text-xs bg-white text-gray-700 rounded-full border border-gray-200"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right side - Actions */}
        <div className="flex flex-col gap-2">
          {article.article_url && (
            <a
              href={article.article_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 bg-white hover:bg-gray-50 rounded-lg border border-gray-200 transition-colors"
              title="Open original article"
            >
              <HiExternalLink className="w-5 h-5 text-gray-700" />
            </a>
          )}

          <button
            onClick={onClear}
            className="p-2 bg-white hover:bg-red-50 rounded-lg border border-gray-200 hover:border-red-300 transition-colors"
            title="Clear selection"
          >
            <HiX className="w-5 h-5 text-gray-700 hover:text-red-600" />
          </button>
        </div>
      </div>
    </div>
  );
};
