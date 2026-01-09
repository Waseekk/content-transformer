/**
 * Article Card Component
 * Beautiful card design with glass-morphism effect
 */

import type { Article } from '../../types';
import { HiCheckCircle } from 'react-icons/hi';

interface ArticleCardProps {
  article: Article;
  isSelected?: boolean;
  onSelect: () => void;
  onPreview?: () => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  isSelected,
  onSelect,
  onPreview,
}) => {
  return (
    <div
      className={`
        relative group
        bg-white rounded-xl border-2 transition-all duration-200
        hover:shadow-lg hover:border-teal-400
        ${isSelected ? 'border-teal-500 shadow-lg ring-2 ring-teal-200' : 'border-gray-200'}
      `}
      onClick={onPreview}
    >
      {/* Left accent border */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${isSelected ? 'bg-teal-500' : 'bg-teal-400 opacity-0 group-hover:opacity-100'} transition-opacity`} />

      {/* Selected badge */}
      {isSelected && (
        <div className="absolute -top-2 -right-2 bg-teal-500 text-white rounded-full p-1">
          <HiCheckCircle className="w-5 h-5" />
        </div>
      )}

      <div className="p-5 pl-6">
        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 font-serif">
          {article.headline}
        </h3>

        {/* Metadata */}
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
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

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {article.tags.slice(0, 3).map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSelect();
            }}
            className={`
              flex-1 px-4 py-2 rounded-lg font-semibold transition-all
              ${isSelected
                ? 'bg-teal-500 text-white'
                : 'bg-teal-50 text-teal-700 hover:bg-teal-100'
              }
            `}
          >
            {isSelected ? '✓ Selected' : 'Select for Translation'}
          </button>

          {article.article_url && (
            <a
              href={article.article_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-4 py-2 border-2 border-gray-200 hover:border-gray-300 rounded-lg text-gray-700 hover:text-gray-900 transition-colors"
            >
              🔗
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
