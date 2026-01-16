/**
 * Content Preview Component - Shows the original English content
 * Clean display with copy and download options
 */

import React, { useState } from 'react';
import { HiClipboard, HiClipboardCheck, HiDownload, HiCheckCircle } from 'react-icons/hi';
import toast from 'react-hot-toast';

interface ContentPreviewProps {
  content: string;
}

export const ContentPreview: React.FC<ContentPreviewProps> = ({ content }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success('Copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'english_content.txt';
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  // Calculate word count
  const wordCount = content.split(/\s+/).filter(Boolean).length;

  return (
    <div className="space-y-4">
      {/* Success Banner */}
      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <HiCheckCircle className="w-6 h-6 text-green-600" />
          <span className="text-sm font-medium text-green-900">
            Content ready! Select formats below to generate news articles.
          </span>
        </div>
      </div>

      {/* Content Display */}
      <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
        <div className="bg-gray-100 px-6 py-3 border-b-2 border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl">📄</span>
            <div>
              <h4 className="font-semibold text-gray-900">English Content</h4>
              <p className="text-xs text-gray-500">{wordCount} words</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium text-gray-700"
              title="Copy to clipboard"
            >
              {copied ? (
                <>
                  <HiClipboardCheck className="w-4 h-4 text-green-600" />
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
              className="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium text-gray-700"
              title="Download"
            >
              <HiDownload className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>
        <div className="p-6 max-h-64 overflow-y-auto bg-gray-50">
          <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
            {content}
          </p>
        </div>
      </div>
    </div>
  );
};
