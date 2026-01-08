/**
 * Format Card Component - Visual card for each content format
 * Features: Edit mode, Copy All, Markdown rendering, Download
 */

import React, { useState, useEffect } from 'react';
import { HiClipboard, HiClipboardCheck, HiDownload, HiPencil, HiCheck, HiX } from 'react-icons/hi';
import ReactMarkdown from 'react-markdown';
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
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content || '');

  // Sync editedContent when content changes (e.g., after generation)
  useEffect(() => {
    if (content) {
      setEditedContent(content);
    }
  }, [content]);

  const handleCopyAll = async () => {
    const textToCopy = isEditing ? editedContent : (content || '');
    if (!textToCopy) return;

    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success(`${title} copied to clipboard!`);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleDownload = () => {
    const textToDownload = isEditing ? editedContent : (content || '');
    if (!textToDownload) return;

    const blob = new Blob([textToDownload], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  const handleEditToggle = () => {
    if (isEditing) {
      // Save changes
      toast.success('Changes saved!');
    }
    setIsEditing(!isEditing);
  };

  const handleCancelEdit = () => {
    setEditedContent(content || '');
    setIsEditing(false);
  };

  const displayContent = isEditing ? editedContent : (content || '');

  return (
    <div
      className={`
        bg-white rounded-2xl border-2 overflow-hidden transition-all duration-300
        ${content ? 'border-teal-300 shadow-xl' : 'border-gray-200 hover:border-gray-300'}
      `}
    >
      {/* Header */}
      <div
        className={`
          px-6 py-5 border-b-2
          ${
            content
              ? `bg-gradient-to-r ${gradientFrom} ${gradientTo} border-teal-300`
              : 'bg-gray-50 border-gray-200'
          }
        `}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{icon}</span>
            <div>
              <h4
                className={`font-bold text-xl ${
                  content ? 'text-white' : 'text-gray-900'
                }`}
              >
                {title}
              </h4>
              <p
                className={`text-sm ${
                  content ? 'text-white/80' : 'text-gray-500'
                }`}
              >
                {description}
              </p>
            </div>
          </div>

          {/* Token Badge */}
          {tokensUsed && (
            <span className="px-4 py-1.5 bg-white/90 text-teal-700 text-sm font-bold rounded-full shadow-sm">
              {tokensUsed} tokens
            </span>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-14 w-14 border-4 border-teal-500 border-t-transparent"></div>
            <p className="mt-5 text-gray-600 font-medium">Generating {title}...</p>
            <p className="text-sm text-gray-400 mt-1">This may take a few seconds</p>
          </div>
        ) : content ? (
          <>
            {/* Action Buttons - Top */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleEditToggle}
                      className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                    >
                      <HiCheck className="w-4 h-4" />
                      Save
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
                    >
                      <HiX className="w-4 h-4" />
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleEditToggle}
                    className="px-4 py-2 bg-amber-100 hover:bg-amber-200 text-amber-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
                  >
                    <HiPencil className="w-4 h-4" />
                    Edit
                  </button>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyAll}
                  className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <HiClipboardCheck className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <HiClipboard className="w-4 h-4" />
                      Copy All
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
            </div>

            {/* Content Display/Edit */}
            <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 overflow-hidden">
              {isEditing ? (
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="w-full min-h-[400px] p-5 text-gray-900 bg-white font-bengali text-base leading-relaxed resize-y focus:outline-none focus:ring-2 focus:ring-teal-300"
                  placeholder="Edit your content here..."
                />
              ) : (
                <div className="p-5 min-h-[300px] max-h-[500px] overflow-y-auto">
                  <div className="prose prose-lg max-w-none font-bengali text-gray-900 leading-relaxed">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => (
                          <p className="mb-4 text-gray-900 leading-relaxed">{children}</p>
                        ),
                        strong: ({ children }) => (
                          <strong className="font-bold text-gray-900">{children}</strong>
                        ),
                      }}
                    >
                      {displayContent}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>

            {/* Word Count */}
            <div className="mt-3 text-right text-sm text-gray-400">
              {displayContent.split(/\s+/).filter(Boolean).length} words
            </div>
          </>
        ) : (
          <div className="py-12 text-center text-gray-400">
            <div className="text-4xl mb-3">📝</div>
            <p className="text-sm">Content will appear here after generation</p>
          </div>
        )}
      </div>
    </div>
  );
};
