/**
 * Format Card Component - Visual card for each content format
 * Features: Edit mode, Copy All (rich text), Markdown rendering, Download (TXT, Word)
 */

import React, { useState, useEffect } from 'react';
import { HiClipboard, HiClipboardCheck, HiDownload, HiPencil, HiCheck, HiX } from 'react-icons/hi';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import { Document, Packer, Paragraph, TextRun } from 'docx';
import { saveAs } from 'file-saver';

interface FormatCardProps {
  title: string;
  icon: string;
  description: string;
  content?: string;
  isLoading?: boolean;
  gradientFrom: string;
  gradientTo: string;
  formatId?: string;
  onContentUpdate?: (formatId: string, newContent: string) => void;
}

/**
 * Convert markdown text to HTML string (handles **bold** formatting)
 */
const markdownToHtml = (markdown: string): string => {
  // Convert **text** to <strong>text</strong>
  let html = markdown.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Convert newlines to paragraphs
  const paragraphs = html.split(/\n\n+/).filter(p => p.trim());
  html = paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');

  return html;
};

/**
 * Convert markdown to plain text (removes ** markers)
 */
const markdownToPlainText = (markdown: string): string => {
  return markdown.replace(/\*\*/g, '');
};

/**
 * Parse markdown and create Word document paragraphs
 */
const parseMarkdownForWord = (markdown: string): Paragraph[] => {
  const paragraphs: Paragraph[] = [];
  const lines = markdown.split(/\n\n+/).filter(line => line.trim());

  for (const line of lines) {
    const textRuns: TextRun[] = [];
    let currentIndex = 0;
    const boldRegex = /\*\*(.+?)\*\*/g;
    let match;

    while ((match = boldRegex.exec(line)) !== null) {
      // Add text before the bold part
      if (match.index > currentIndex) {
        const beforeText = line.slice(currentIndex, match.index);
        if (beforeText) {
          textRuns.push(new TextRun({ text: beforeText, size: 24 }));
        }
      }

      // Add bold text
      textRuns.push(new TextRun({
        text: match[1],
        bold: true,
        size: 24
      }));

      currentIndex = match.index + match[0].length;
    }

    // Add remaining text after last bold
    if (currentIndex < line.length) {
      const remainingText = line.slice(currentIndex);
      if (remainingText) {
        textRuns.push(new TextRun({ text: remainingText, size: 24 }));
      }
    }

    // If no bold markers found, add the whole line
    if (textRuns.length === 0 && line.trim()) {
      textRuns.push(new TextRun({ text: line, size: 24 }));
    }

    if (textRuns.length > 0) {
      paragraphs.push(new Paragraph({
        children: textRuns,
        spacing: { after: 200 },
      }));
    }
  }

  return paragraphs;
};

export const FormatCard: React.FC<FormatCardProps> = ({
  title,
  icon,
  description,
  content,
  isLoading,
  gradientFrom,
  gradientTo,
  formatId,
  onContentUpdate,
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

  /**
   * Copy content as rich text (HTML) with bold formatting preserved
   */
  const handleCopyAll = async () => {
    const textToCopy = isEditing ? editedContent : (content || '');
    if (!textToCopy) return;

    try {
      // Convert markdown to HTML for rich text
      const htmlContent = markdownToHtml(textToCopy);
      const plainContent = markdownToPlainText(textToCopy);

      // Try to copy as both HTML and plain text
      if (navigator.clipboard && typeof ClipboardItem !== 'undefined') {
        const htmlBlob = new Blob([htmlContent], { type: 'text/html' });
        const textBlob = new Blob([plainContent], { type: 'text/plain' });

        await navigator.clipboard.write([
          new ClipboardItem({
            'text/html': htmlBlob,
            'text/plain': textBlob,
          }),
        ]);
      } else {
        // Fallback for browsers that don't support ClipboardItem
        await navigator.clipboard.writeText(plainContent);
      }

      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success(`${title} copied with formatting!`);
    } catch (err) {
      // Fallback to plain text
      try {
        const plainContent = markdownToPlainText(textToCopy);
        await navigator.clipboard.writeText(plainContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        toast.success(`${title} copied to clipboard!`);
      } catch {
        toast.error('Failed to copy');
      }
    }
  };

  /**
   * Download content as Word document (.docx) with bold formatting
   */
  const handleDownloadWord = async () => {
    const textToDownload = isEditing ? editedContent : (content || '');
    if (!textToDownload) return;

    try {
      const paragraphs = parseMarkdownForWord(textToDownload);

      const doc = new Document({
        sections: [{
          properties: {},
          children: paragraphs,
        }],
      });

      const blob = await Packer.toBlob(doc);
      const filename = `${title.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.docx`;
      saveAs(blob, filename);
      toast.success('Downloaded as Word!');
    } catch (err) {
      console.error('Word export error:', err);
      toast.error('Failed to create Word document');
    }
  };

  const handleEditToggle = () => {
    if (isEditing) {
      // Save changes - update parent state
      if (onContentUpdate && formatId) {
        onContentUpdate(formatId, editedContent);
      }
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
                {/* Copy All - Rich Text */}
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

                {/* Download as Word */}
                <button
                  onClick={handleDownloadWord}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                  title="Download as Word document"
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
