/**
 * Content Preview Component - Collapsible English content display
 */

import React, { useState } from 'react';
import { HiChevronDown, HiDocumentText } from 'react-icons/hi';

interface ContentPreviewProps {
  content: string;
}

export const ContentPreview: React.FC<ContentPreviewProps> = ({ content }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate word count
  const wordCount = content.split(/\s+/).filter(Boolean).length;

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <HiDocumentText className="w-5 h-5 text-blue-600" />
          </div>
          <div className="text-left">
            <h4 className="font-semibold text-gray-900">English Content</h4>
            <p className="text-sm text-gray-500">{wordCount} words</p>
          </div>
        </div>
        <div className={`
          w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center
          transition-transform duration-200
          ${isExpanded ? 'rotate-180' : ''}
        `}>
          <HiChevronDown className="w-5 h-5 text-gray-500" />
        </div>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-100 animate-in slide-in-from-top-2 duration-200">
          <div className="mt-4 p-4 bg-gray-50 rounded-xl max-h-64 overflow-y-auto">
            <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
              {content}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
