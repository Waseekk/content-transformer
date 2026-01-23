/**
 * Enhancement Section - Multi-format content generation
 * State persists across tab changes via Zustand store
 */

import React from 'react';
import { FormatCard } from './FormatCard';
import { useEnhance } from '../../hooks/useEnhancement';
import { useAppStore } from '../../store/useAppStore';
import { HiSparkles, HiNewspaper, HiBookOpen } from 'react-icons/hi';

interface EnhancementSectionProps {
  translatedText: string;
  englishContent?: string;
}

export const EnhancementSection: React.FC<EnhancementSectionProps> = ({
  translatedText,
  englishContent,
}) => {
  const enhance = useEnhance();
  const {
    selectedFormats,
    toggleFormat,
    currentEnhancements,
    addEnhancement,
  } = useAppStore();

  // Format definitions
  const formats = [
    {
      id: 'hard_news',
      title: 'হার্ড নিউজ',
      subtitle: 'বাংলার কলম্বাস',
      icon: HiNewspaper,
      description: 'Professional factual reporting',
      color: 'blue',
    },
    {
      id: 'soft_news',
      title: 'সফট নিউজ',
      subtitle: 'বাংলার কলম্বাস',
      icon: HiBookOpen,
      description: 'Literary travel feature',
      color: 'teal',
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

      response.formats.forEach((result: any) => {
        addEnhancement(result.format_type, {
          format_type: result.format_type,
          content: result.content,
          tokens_used: result.tokens_used,
          timestamp: new Date().toISOString(),
        });
      });
    } catch {
      // Enhancement failed - error handled by mutation
    }
  };

  const isDisabled = !translatedText || selectedFormats.length === 0;

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
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
            <HiSparkles className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Generate News Articles
            </h3>
            <p className="text-sm text-gray-500">
              Select format(s) and generate professional Bengali news
            </p>
          </div>
        </div>

        {/* Format Selection */}
        <div className="flex flex-wrap gap-3 mb-5">
          {formats.map((format) => {
            const isSelected = selectedFormats.includes(format.id);
            const Icon = format.icon;
            return (
              <button
                key={format.id}
                onClick={() => toggleFormat(format.id)}
                className={`
                  flex items-center gap-3 px-5 py-3 rounded-xl font-medium transition-all border-2
                  ${isSelected
                    ? format.color === 'blue'
                      ? 'bg-blue-500 text-white border-blue-500 shadow-md'
                      : 'bg-teal-500 text-white border-teal-500 shadow-md'
                    : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-semibold">{format.title}</p>
                  <p className={`text-xs ${isSelected ? 'text-white/80' : 'text-gray-500'}`}>
                    {format.subtitle}
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Generate Button */}
        <button
          onClick={handleEnhance}
          disabled={isDisabled || enhance.isPending}
          className={`
            inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all
            ${isDisabled || enhance.isPending
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:scale-[1.02]'
            }
          `}
        >
          {enhance.isPending ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <HiSparkles className="w-5 h-5" />
              Generate {selectedFormats.length > 0 ? `(${selectedFormats.length})` : ''}
            </>
          )}
        </button>
      </div>

      {/* Format Cards */}
      {selectedFormats.length > 0 && (
        <div className="flex flex-col gap-6">
          {selectedFormats.map((formatId) => {
            const format = formats.find((f) => f.id === formatId);
            if (!format) return null;

            const result = currentEnhancements[formatId];
            const Icon = format.icon;

            return (
              <FormatCard
                key={formatId}
                formatId={formatId}
                title={format.title}
                subtitle={format.subtitle}
                icon={Icon}
                description={format.description}
                content={result?.content}
                englishContent={englishContent}
                isLoading={enhance.isPending && !result}
                color={format.color}
                onContentUpdate={handleContentUpdate}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
