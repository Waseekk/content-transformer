/**
 * Format Card Component - Premium card for each content format
 * Features: Edit mode, Copy All (rich text), Markdown rendering, Download (Word with English)
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiClipboard, HiClipboardCheck, HiDownload, HiPencil, HiCheck, HiX } from 'react-icons/hi';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx';
import { saveAs } from 'file-saver';
import type { IconType } from 'react-icons';
import { AILoader } from '../ui';
import { useAuth } from '../../contexts/AuthContext';

interface FormatCardProps {
  title: string;
  subtitle?: string;
  icon: IconType;
  description: string;
  content?: string;
  englishContent?: string;
  isLoading?: boolean;
  color: string;
  formatId?: string;
  onContentUpdate?: (formatId: string, newContent: string) => void;
}

/**
 * Convert markdown text to HTML string (handles **bold** formatting)
 * Uses 's' flag to match across newlines
 */
const markdownToHtml = (markdown: string): string => {
  // Replace ** markers - use [\s\S] to match across newlines
  let html = markdown.replace(/\*\*([\s\S]+?)\*\*/g, '<strong>$1</strong>');
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
 * Get current date in Bengali format (e.g., "২০ জানুয়ারি ২০২৬")
 */
const getBengaliDate = (): string => {
  const bengaliMonths = [
    'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
    'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
  ];
  const bengaliDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];

  const now = new Date();
  const day = String(now.getDate()).split('').map(d => bengaliDigits[parseInt(d)]).join('');
  const month = bengaliMonths[now.getMonth()];
  const year = String(now.getFullYear()).split('').map(d => bengaliDigits[parseInt(d)]).join('');

  return `${day} ${month} ${year}`;
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
      if (match.index > currentIndex) {
        const beforeText = line.slice(currentIndex, match.index);
        if (beforeText) {
          textRuns.push(new TextRun({ text: beforeText, size: 24 }));
        }
      }
      textRuns.push(new TextRun({
        text: match[1],
        bold: true,
        size: 24
      }));
      currentIndex = match.index + match[0].length;
    }

    if (currentIndex < line.length) {
      const remainingText = line.slice(currentIndex);
      if (remainingText) {
        textRuns.push(new TextRun({ text: remainingText, size: 24 }));
      }
    }

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
  subtitle,
  icon: Icon,
  description,
  content,
  englishContent,
  isLoading,
  color,
  formatId,
  onContentUpdate,
}) => {
  const { userConfig } = useAuth();
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content || '');

  // Get UI settings from user config
  const hideFormatLabels = userConfig?.ui_settings?.hide_format_labels ?? false;
  const hideMainContentExport = userConfig?.ui_settings?.hide_main_content_export ?? false;
  const downloadPrefix = userConfig?.ui_settings?.download_prefix || userConfig?.client?.name || 'Content';

  useEffect(() => {
    if (content) {
      setEditedContent(content);
    }
  }, [content]);

  const handleCopyAll = async () => {
    const textToCopy = isEditing ? editedContent : (content || '');
    if (!textToCopy) return;

    try {
      const htmlContent = markdownToHtml(textToCopy);
      const plainContent = markdownToPlainText(textToCopy);

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
        await navigator.clipboard.writeText(plainContent);
      }

      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success('Copied with formatting!');
    } catch (err) {
      try {
        const plainContent = markdownToPlainText(textToCopy);
        await navigator.clipboard.writeText(plainContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        toast.success('Copied to clipboard!');
      } catch {
        toast.error('Failed to copy');
      }
    }
  };

  /**
   * Download content as Word document with English content included
   * Respects client UI settings for hiding main content and custom filename prefix
   */
  const handleDownloadWord = async () => {
    const textToDownload = isEditing ? editedContent : (content || '');
    if (!textToDownload) return;

    try {
      const sections: Paragraph[] = [];

      // Add Main Content section first (if available and not hidden by client settings)
      if (englishContent && !hideMainContentExport) {
        // Main content section header
        sections.push(new Paragraph({
          children: [new TextRun({ text: 'MAIN CONTENT', bold: true, size: 28 })],
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 300 },
        }));

        // Divider line
        sections.push(new Paragraph({
          children: [new TextRun({ text: '─'.repeat(50), color: '999999', size: 20 })],
          spacing: { after: 200 },
        }));

        // English content paragraphs
        const englishParagraphs = englishContent.split(/\n\n+/).filter(p => p.trim());
        for (const para of englishParagraphs) {
          sections.push(new Paragraph({
            children: [new TextRun({ text: para, size: 22 })],
            spacing: { after: 200 },
          }));
        }

        // Spacer between sections
        sections.push(new Paragraph({
          children: [new TextRun({ text: '' })],
          spacing: { after: 400 },
        }));

        // Another divider
        sections.push(new Paragraph({
          children: [new TextRun({ text: '═'.repeat(50), color: '666666', size: 20 })],
          spacing: { after: 400 },
        }));
      }

      // Add Bengali News section header (only if not hiding format labels)
      if (!hideFormatLabels) {
        const bengaliTitle = title === 'হার্ড নিউজ' ? 'হার্ড নিউজ (HARD NEWS)' : 'সফট নিউজ (SOFT NEWS)';
        sections.push(new Paragraph({
          children: [new TextRun({ text: bengaliTitle, bold: true, size: 28 })],
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 300 },
        }));

        // Divider line
        sections.push(new Paragraph({
          children: [new TextRun({ text: '─'.repeat(50), color: '999999', size: 20 })],
          spacing: { after: 200 },
        }));
      }

      // Bengali content with markdown parsing
      const bengaliParagraphs = parseMarkdownForWord(textToDownload);
      sections.push(...bengaliParagraphs);

      const doc = new Document({
        sections: [{
          properties: {},
          children: sections,
        }],
      });

      const blob = await Packer.toBlob(doc);
      // Dynamic filename: uses download_prefix or client name, excludes format type if hidden
      let filename: string;
      if (hideFormatLabels) {
        // Without format type: ClientName-২০ জানুয়ারি ২০২৬.docx
        filename = `${downloadPrefix}-${getBengaliDate()}.docx`;
      } else {
        // With format type: বাংলার কলম্বাস-হার্ড নিউজ-২০ জানুয়ারি ২০২৬.docx
        const formatTypeBengali = title === 'হার্ড নিউজ' ? 'হার্ড নিউজ' : 'সফট নিউজ';
        filename = `${downloadPrefix}-${formatTypeBengali}-${getBengaliDate()}.docx`;
      }
      saveAs(blob, filename);
      toast.success(hideMainContentExport ? 'Downloaded!' : 'Downloaded with Main Content!');
    } catch {
      toast.error('Failed to create Word document');
    }
  };

  const handleEditToggle = () => {
    if (isEditing) {
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

  // Color classes
  const colorClasses = {
    blue: {
      bg: 'bg-gradient-to-r from-blue-500 to-blue-600',
      bgLight: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-200',
      glow: 'shadow-blue-200/50',
    },
    teal: {
      bg: 'bg-gradient-to-r from-ai-primary to-ai-secondary',
      bgLight: 'bg-ai-primary/10',
      text: 'text-ai-primary',
      border: 'border-ai-primary/20',
      glow: 'shadow-ai-primary/30',
    },
  }[color] || { bg: 'bg-gray-500', bgLight: 'bg-gray-50', text: 'text-gray-600', border: 'border-gray-200', glow: '' };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        bg-white rounded-2xl border-2 overflow-hidden transition-all duration-300
        ${content ? `${colorClasses.border} shadow-premium hover:shadow-premium-lg` : 'border-gray-200'}
      `}
    >
      {/* Header */}
      <div className={`
        px-6 py-5 border-b-2
        ${content ? `${colorClasses.bg} ${colorClasses.border}` : 'bg-gray-50 border-gray-200'}
      `}>
        <div className="flex items-center gap-4">
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            className={`
              w-12 h-12 rounded-xl flex items-center justify-center
              ${content ? 'bg-white/20 shadow-lg' : colorClasses.bgLight}
            `}
          >
            <Icon className={`w-6 h-6 ${content ? 'text-white' : colorClasses.text}`} />
          </motion.div>
          <div>
            {/* Hide title if hideFormatLabels is enabled */}
            {!hideFormatLabels && (
              <h4 className={`font-bold text-xl ${content ? 'text-white' : 'text-gray-900'}`}>
                {title}
              </h4>
            )}
            {hideFormatLabels ? (
              <p className={`text-sm ${content ? 'text-white/80' : 'text-gray-500'}`}>
                {description}
              </p>
            ) : subtitle && (
              <p className={`text-sm ${content ? 'text-white/80' : 'text-gray-500'}`}>
                {subtitle} • {description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <AILoader variant="neural" size="lg" text={`Generating ${title}...`} />
          </div>
        ) : content ? (
          <>
            {/* Action Buttons */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <AnimatePresence mode="wait">
                  {isEditing ? (
                    <motion.div
                      key="editing"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      className="flex items-center gap-2"
                    >
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleEditToggle}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-medium transition-all shadow-sm"
                      >
                        <HiCheck className="w-4 h-4" />
                        Save
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleCancelEdit}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-all"
                      >
                        <HiX className="w-4 h-4" />
                        Cancel
                      </motion.button>
                    </motion.div>
                  ) : (
                    <motion.button
                      key="edit"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleEditToggle}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 hover:bg-amber-200 text-amber-700 rounded-xl font-medium transition-all"
                    >
                      <HiPencil className="w-4 h-4" />
                      Edit
                    </motion.button>
                  )}
                </AnimatePresence>
              </div>

              <div className="flex items-center gap-2">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCopyAll}
                  className={`inline-flex items-center gap-2 px-4 py-2 ${colorClasses.bg} text-white rounded-xl font-medium transition-all shadow-sm`}
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
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleDownloadWord}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white rounded-xl font-medium transition-all shadow-sm"
                  title="Download as Word (includes English content)"
                >
                  <HiDownload className="w-4 h-4" />
                  Download
                </motion.button>
              </div>
            </div>

            {/* Content Display/Edit */}
            <div className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
              <AnimatePresence mode="wait">
                {isEditing ? (
                  <motion.textarea
                    key="textarea"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="w-full min-h-[400px] p-5 text-gray-900 bg-white font-bengali text-base leading-relaxed resize-y focus:outline-none focus:ring-2 focus:ring-ai-primary/30"
                    placeholder="Edit your content here..."
                  />
                ) : (
                  <motion.div
                    key="preview"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="p-5 min-h-[300px] max-h-[500px] overflow-y-auto"
                  >
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
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Word Count */}
            <div className="mt-3 flex items-center justify-between text-sm text-gray-400">
              <span>{displayContent.split(/\s+/).filter(Boolean).length} words</span>
            </div>
          </>
        ) : (
          <div className="py-12 text-center text-gray-400">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className={`w-16 h-16 mx-auto mb-4 rounded-full ${colorClasses.bgLight} flex items-center justify-center`}
            >
              <Icon className={`w-8 h-8 ${colorClasses.text}`} />
            </motion.div>
            <p className="font-medium">Content will appear here</p>
            <p className="text-sm mt-1">Select this format and click "Generate"</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};
