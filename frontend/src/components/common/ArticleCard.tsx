/**
 * Article Card Component - Modern design with entrance animation
 */

import { motion } from 'framer-motion';
import type { Article } from '../../types';
import { HiCheckCircle, HiNewspaper, HiClock, HiGlobe, HiExternalLink } from 'react-icons/hi';

interface ArticleCardProps {
  article: Article;
  isSelected?: boolean;
  onSelect: () => void;
  onPreview?: () => void;
  index?: number;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  isSelected,
  onSelect,
  onPreview,
  index = 0,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05, ease: 'easeOut' }}
      whileHover={{ y: -4 }}
      className={`
        relative group overflow-hidden
        bg-white rounded-2xl transition-shadow duration-300
        hover:shadow-xl
        ${isSelected
          ? 'ring-2 ring-teal-500 shadow-lg shadow-teal-100'
          : 'shadow-sm hover:shadow-lg border border-gray-100'
        }
      `}
      onClick={onPreview}
    >
      {/* Top gradient accent */}
      <div className={`
        absolute top-0 left-0 right-0 h-1
        ${isSelected
          ? 'bg-gradient-to-r from-teal-500 to-teal-400'
          : 'bg-gradient-to-r from-gray-200 to-gray-100 group-hover:from-teal-400 group-hover:to-teal-300'
        }
        transition-all duration-300
      `} />

      {/* Selected badge */}
      {isSelected && (
        <div className="absolute top-3 right-3 bg-teal-500 text-white rounded-full p-1.5 shadow-lg">
          <HiCheckCircle className="w-5 h-5" />
        </div>
      )}

      <div className="p-6">
        {/* Publisher badge */}
        <div className="flex items-center gap-2 mb-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
            <HiNewspaper className="w-3.5 h-3.5" />
            {article.publisher}
          </span>
          {article.country && article.country.toLowerCase() !== 'unknown' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-medium">
              <HiGlobe className="w-3 h-3" />
              {article.country}
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-snug group-hover:text-gray-700 transition-colors">
          {article.headline}
        </h3>

        {/* Time */}
        <div className="flex items-center gap-1.5 text-sm text-gray-500 mb-4">
          <HiClock className="w-4 h-4" />
          <span>{article.published_time || 'N/A'}</span>
        </div>

        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-5">
            {article.tags.slice(0, 3).map((tag, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 text-xs bg-gray-50 text-gray-600 rounded-lg border border-gray-100"
              >
                {tag}
              </span>
            ))}
            {article.tags.length > 3 && (
              <span className="px-2.5 py-1 text-xs text-gray-400">
                +{article.tags.length - 3} more
              </span>
            )}
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
              flex-1 px-4 py-2.5 rounded-xl font-semibold transition-all duration-200
              ${isSelected
                ? 'bg-teal-500 text-white shadow-md shadow-teal-200'
                : 'bg-gray-100 text-gray-700 hover:bg-teal-500 hover:text-white hover:shadow-md hover:shadow-teal-200'
              }
            `}
          >
            {isSelected ? 'Selected' : 'Select'}
          </button>

          {article.article_url && (
            <a
              href={article.article_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-600 hover:text-gray-800 transition-all duration-200 flex items-center justify-center"
              title="Open original article"
            >
              <HiExternalLink className="w-5 h-5" />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
};
