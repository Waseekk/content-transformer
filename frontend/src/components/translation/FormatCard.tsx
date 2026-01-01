/**
 * Format Card Component - Visual card for each content format
 */

import React, { useState } from 'react';
import { HiClipboard, HiClipboardCheck, HiDownload } from 'react-icons/hi';
import toast from 'react-hot-toast';

interface FormatCardProps {
  title: string;
  icon: string;
  description: string;
  content?: string;
  tokensUsed?: number;
  isLoading?: boolean;
  gradientFrom: string;
  gradientTo: string;
}

export const FormatCard: React.FC<FormatCardProps> = ({
  title,
  icon,
  description,
  content,
  tokensUsed,
  isLoading,
  gradientFrom,
  gradientTo,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success(`${title} copied!`);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleDownload = () => {
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  return (
    <div
      className={`
        bg-white rounded-xl border-2 overflow-hidden transition-all duration-300
        ${content ? 'border-teal-300 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
      `}
    >
      {/* Header */}
      <div
        className={`
          px-6 py-4 border-b-2
          ${
            content
              ? `bg-gradient-to-r ${gradientFrom} ${gradientTo} border-teal-300`
              : 'bg-gray-50 border-gray-200'
          }
        `}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">{icon}</span>
              <h4
                className={`font-bold text-lg ${
                  content ? 'text-white' : 'text-gray-900'
                }`}
              >
                {title}
              </h4>
            </div>
            <p
              className={`text-sm ${
                content ? 'text-white/90' : 'text-gray-600'
              }`}
            >
              {description}
            </p>
          </div>

          {/* Token Badge */}
          {tokensUsed && (
            <span className="px-3 py-1 bg-white text-teal-700 text-xs font-semibold rounded-full">
              {tokensUsed} tokens
            </span>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
            <p className="mt-4 text-gray-600 text-sm">Generating {title}...</p>
          </div>
        ) : content ? (
          <>
            {/* Content Text */}
            <div className="max-h-64 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed font-bengali">
                {content}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleCopy}
                className="flex-1 px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {copied ? (
                  <>
                    <HiClipboardCheck className="w-4 h-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <HiClipboard className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>

              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                <HiDownload className="w-4 h-4" />
                Download
              </button>
            </div>
          </>
        ) : (
          <div className="py-8 text-center text-gray-400">
            <p className="text-sm">Content will appear here after generation</p>
          </div>
        )}
      </div>
    </div>
  );
};
