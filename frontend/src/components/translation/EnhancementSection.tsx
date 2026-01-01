/**
 * Enhancement Section - Multi-format content generation
 */

import React, { useState } from 'react';
import { FormatCard } from './FormatCard';
import { useEnhance } from '../../hooks/useEnhancement';

interface EnhancementSectionProps {
  translatedText: string;
}

export const EnhancementSection: React.FC<EnhancementSectionProps> = ({
  translatedText,
}) => {
  const enhance = useEnhance();
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [results, setResults] = useState<Record<string, any>>({});

  // Format definitions matching backend
  const formats = [
    {
      id: 'newspaper',
      title: 'Newspaper Article',
      icon: '📰',
      description: 'Formal newspaper-style article',
      gradientFrom: 'from-blue-500',
      gradientTo: 'to-blue-600',
    },
    {
      id: 'blog',
      title: 'Blog Post',
      icon: '✍️',
      description: 'Personal blog-style content',
      gradientFrom: 'from-purple-500',
      gradientTo: 'to-purple-600',
    },
    {
      id: 'facebook',
      title: 'Facebook Post',
      icon: '👥',
      description: 'Social media post (100-150 words)',
      gradientFrom: 'from-blue-600',
      gradientTo: 'to-blue-700',
    },
    {
      id: 'instagram',
      title: 'Instagram Caption',
      icon: '📸',
      description: 'Caption with hashtags (50-100 words)',
      gradientFrom: 'from-pink-500',
      gradientTo: 'to-pink-600',
    },
    {
      id: 'hard_news',
      title: 'Hard News (BC News)',
      icon: '🎯',
      description: 'Professional factual reporting',
      gradientFrom: 'from-red-500',
      gradientTo: 'to-red-600',
    },
    {
      id: 'soft_news',
      title: 'Soft News (BC News)',
      icon: '🌟',
      description: 'Literary travel feature',
      gradientFrom: 'from-teal-500',
      gradientTo: 'to-teal-600',
    },
  ];

  const toggleFormat = (formatId: string) => {
    setSelectedFormats((prev) =>
      prev.includes(formatId)
        ? prev.filter((id) => id !== formatId)
        : [...prev, formatId]
    );
  };

  const handleEnhance = async () => {
    if (selectedFormats.length === 0) {
      return;
    }

    try {
      const response = await enhance.mutateAsync({
        text: translatedText,
        formats: selectedFormats,
      });

      // Update results with generated content
      const newResults: Record<string, any> = {};
      response.results.forEach((result: any) => {
        newResults[result.format_type] = result;
      });
      setResults(newResults);
    } catch (error) {
      console.error('Enhancement failed:', error);
    }
  };

  const isDisabled = !translatedText || selectedFormats.length === 0;

  return (
    <div className="mt-8 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          ✨ Content Enhancement
        </h3>
        <p className="text-gray-700 mb-4">
          Generate multiple format variations from your translated content
        </p>

        {/* Format Selection */}
        <div className="flex flex-wrap gap-2 mb-4">
          {formats.map((format) => (
            <button
              key={format.id}
              onClick={() => toggleFormat(format.id)}
              className={`
                px-4 py-2 rounded-lg font-semibold transition-all
                ${
                  selectedFormats.includes(format.id)
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-purple-300'
                }
              `}
            >
              {format.icon} {format.title}
            </button>
          ))}
        </div>

        {/* Generate Button */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleEnhance}
            disabled={isDisabled || enhance.isPending}
            className={`
              px-8 py-3 rounded-lg font-bold transition-all
              ${
                isDisabled || enhance.isPending
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-xl transform hover:scale-105'
              }
            `}
          >
            {enhance.isPending ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating...
              </span>
            ) : (
              `🚀 Generate ${selectedFormats.length} Format${selectedFormats.length !== 1 ? 's' : ''}`
            )}
          </button>

          {selectedFormats.length > 0 && (
            <span className="text-sm text-gray-600">
              {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
            </span>
          )}
        </div>
      </div>

      {/* Format Cards Grid */}
      {selectedFormats.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {selectedFormats.map((formatId) => {
            const format = formats.find((f) => f.id === formatId);
            if (!format) return null;

            const result = results[formatId];

            return (
              <FormatCard
                key={formatId}
                title={format.title}
                icon={format.icon}
                description={format.description}
                content={result?.content}
                tokensUsed={result?.tokens_used}
                isLoading={enhance.isPending && !result}
                gradientFrom={format.gradientFrom}
                gradientTo={format.gradientTo}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
