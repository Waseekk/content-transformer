/**
 * Enhancement Section - Multi-format content generation
 * State persists across tab changes via Zustand store
 */

import React from 'react';
import { FormatCard } from './FormatCard';
import { useEnhance } from '../../hooks/useEnhancement';
import { useAppStore } from '../../store/useAppStore';

interface EnhancementSectionProps {
  translatedText: string;
}

export const EnhancementSection: React.FC<EnhancementSectionProps> = ({
  translatedText,
}) => {
  const enhance = useEnhance();
  const {
    selectedFormats,
    toggleFormat,
    currentEnhancements,
    addEnhancement,
  } = useAppStore();

  // Format definitions - Only hard_news and soft_news for deployment
  const formats = [
    {
      id: 'hard_news',
      title: 'হার্ড নিউজ (বাংলার কলম্বাস)',
      icon: '📄',
      description: 'পেশাদার তথ্যভিত্তিক সংবাদ - Professional factual reporting',
      gradientFrom: 'from-blue-600',
      gradientTo: 'to-blue-700',
    },
    {
      id: 'soft_news',
      title: 'সফট নিউজ (বাংলার কলম্বাস)',
      icon: '✍️',
      description: 'বর্ণনামূলক ভ্রমণ ফিচার - Literary travel feature',
      gradientFrom: 'from-teal-500',
      gradientTo: 'to-teal-600',
    },
  ];

  const handleEnhance = async () => {
    if (selectedFormats.length === 0) {
      return;
    }

    try {
      const response = await enhance.mutateAsync({
        text: translatedText,
        headline: 'News Article',
        formats: selectedFormats,
      });

      // Store results in global state so they persist across tab changes
      response.formats.forEach((result: any) => {
        addEnhancement(result.format_type, {
          format_type: result.format_type,
          content: result.content,
          tokens_used: result.tokens_used,
          timestamp: new Date().toISOString(),
        });
      });
    } catch (error) {
      console.error('Enhancement failed:', error);
    }
  };

  const isDisabled = !translatedText || selectedFormats.length === 0;

  // Handle content updates from FormatCard edits
  const handleContentUpdate = (formatId: string, newContent: string) => {
    const existing = currentEnhancements[formatId];
    if (existing) {
      addEnhancement(formatId, {
        ...existing,
        content: newContent,
      });
    }
  };

  return (
    <div className="mt-8 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          ✨ Generate News Articles
        </h3>
        <p className="text-gray-700 mb-4">
          Select format(s) and generate professional Bengali news articles
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

      {/* Format Cards - Vertical Stack */}
      {selectedFormats.length > 0 && (
        <div className="flex flex-col gap-6">
          {selectedFormats.map((formatId) => {
            const format = formats.find((f) => f.id === formatId);
            if (!format) return null;

            const result = currentEnhancements[formatId];

            return (
              <FormatCard
                key={formatId}
                formatId={formatId}
                title={format.title}
                icon={format.icon}
                description={format.description}
                content={result?.content}
                isLoading={enhance.isPending && !result}
                gradientFrom={format.gradientFrom}
                gradientTo={format.gradientTo}
                onContentUpdate={handleContentUpdate}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
