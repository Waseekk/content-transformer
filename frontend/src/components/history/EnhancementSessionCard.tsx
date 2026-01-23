/**
 * Enhancement Session Card - Expandable card showing enhancement sessions
 * Features: Expand/collapse, preview content, download Word files
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HiChevronDown,
  HiChevronUp,
  HiDownload,
  HiClipboard,
  HiClipboardCheck,
  HiNewspaper,
  HiDocumentText,
} from 'react-icons/hi';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx';
import { saveAs } from 'file-saver';
import type { EnhancementSession, EnhancementData } from '../../hooks/useEnhancementHistory';

interface EnhancementSessionCardProps {
  session: EnhancementSession;
}

/**
 * Get current date in Bengali format (e.g., "20 January 2026")
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

/**
 * Convert markdown to plain text
 */
const markdownToPlainText = (markdown: string): string => {
  return markdown.replace(/\*\*/g, '');
};

/**
 * Convert markdown text to HTML string
 */
const markdownToHtml = (markdown: string): string => {
  let html = markdown.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  const paragraphs = html.split(/\n\n+/).filter(p => p.trim());
  html = paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('');
  return html;
};

interface FormatBoxProps {
  title: string;
  formatType: 'hard_news' | 'soft_news';
  data: EnhancementData;
  englishContent: string | null;
  fullWidth?: boolean;
}

const FormatBox: React.FC<FormatBoxProps> = ({ title, formatType, data, englishContent, fullWidth = false }) => {
  const [copied, setCopied] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const handleCopy = async () => {
    try {
      const htmlContent = markdownToHtml(data.content);
      const plainContent = markdownToPlainText(data.content);

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
    } catch {
      toast.error('Failed to copy');
    }
  };

  const handleDownload = async () => {
    try {
      const sections: Paragraph[] = [];

      // Add Main Content section first (if available)
      if (englishContent) {
        sections.push(new Paragraph({
          children: [new TextRun({ text: 'MAIN CONTENT', bold: true, size: 28 })],
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 300 },
        }));

        sections.push(new Paragraph({
          children: [new TextRun({ text: '─'.repeat(50), color: '999999', size: 20 })],
          spacing: { after: 200 },
        }));

        const englishParagraphs = englishContent.split(/\n\n+/).filter(p => p.trim());
        for (const para of englishParagraphs) {
          sections.push(new Paragraph({
            children: [new TextRun({ text: para, size: 22 })],
            spacing: { after: 200 },
          }));
        }

        sections.push(new Paragraph({
          children: [new TextRun({ text: '' })],
          spacing: { after: 400 },
        }));

        sections.push(new Paragraph({
          children: [new TextRun({ text: '═'.repeat(50), color: '666666', size: 20 })],
          spacing: { after: 400 },
        }));
      }

      // Add Bengali News section
      const bengaliTitle = formatType === 'hard_news' ? 'হার্ড নিউজ (HARD NEWS)' : 'সফট নিউজ (SOFT NEWS)';
      sections.push(new Paragraph({
        children: [new TextRun({ text: bengaliTitle, bold: true, size: 28 })],
        heading: HeadingLevel.HEADING_1,
        spacing: { after: 300 },
      }));

      sections.push(new Paragraph({
        children: [new TextRun({ text: '─'.repeat(50), color: '999999', size: 20 })],
        spacing: { after: 200 },
      }));

      const bengaliParagraphs = parseMarkdownForWord(data.content);
      sections.push(...bengaliParagraphs);

      const doc = new Document({
        sections: [{
          properties: {},
          children: sections,
        }],
      });

      const blob = await Packer.toBlob(doc);
      const formatTypeBengali = formatType === 'hard_news' ? 'হার্ড নিউজ' : 'সফট নিউজ';
      const filename = `বাংলার কলম্বাস-${formatTypeBengali}-${getBengaliDate()}.docx`;
      saveAs(blob, filename);
      toast.success('Downloaded with Main Content!');
    } catch {
      toast.error('Failed to create Word document');
    }
  };

  const colorClasses = formatType === 'hard_news'
    ? { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', button: 'bg-blue-500 hover:bg-blue-600' }
    : { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-700', button: 'bg-teal-500 hover:bg-teal-600' };

  return (
    <div className={`${fullWidth ? 'w-full' : 'flex-1'} rounded-xl border ${colorClasses.border} overflow-hidden`}>
      {/* Header */}
      <div className={`px-4 py-3 ${colorClasses.bg} flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          {formatType === 'hard_news' ? (
            <HiNewspaper className={`w-5 h-5 ${colorClasses.text}`} />
          ) : (
            <HiDocumentText className={`w-5 h-5 ${colorClasses.text}`} />
          )}
          <span className={`font-semibold ${colorClasses.text}`}>{title}</span>
          <span className="text-xs text-gray-500">{data.word_count} words</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg hover:bg-white/50 transition-colors"
            title="Copy to clipboard"
          >
            {copied ? (
              <HiClipboardCheck className="w-4 h-4 text-green-600" />
            ) : (
              <HiClipboard className="w-4 h-4 text-gray-600" />
            )}
          </button>
          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg hover:bg-white/50 transition-colors"
            title="Download as Word"
          >
            <HiDownload className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Preview Toggle */}
      <div className="px-4 py-2 border-t border-gray-100">
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          {showPreview ? (
            <>
              <HiChevronUp className="w-4 h-4" />
              Hide Preview
            </>
          ) : (
            <>
              <HiChevronDown className="w-4 h-4" />
              Show Preview
            </>
          )}
        </button>
      </div>

      {/* Content Preview */}
      <AnimatePresence>
        {showPreview && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 max-h-[300px] overflow-y-auto">
              <div className="prose prose-sm max-w-none font-bengali text-gray-800">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => (
                      <p className="mb-3 text-gray-800 leading-relaxed text-sm">{children}</p>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-bold text-gray-900">{children}</strong>
                    ),
                  }}
                >
                  {data.content}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/**
 * Convert UTC date to Bangladesh Time (UTC+6)
 */
const toBangladeshTime = (dateStr: string): Date => {
  const date = new Date(dateStr);
  // Add 6 hours for Bangladesh timezone
  return new Date(date.getTime() + (6 * 60 * 60 * 1000));
};

export const EnhancementSessionCard: React.FC<EnhancementSessionCardProps> = ({ session }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatTime = (dateStr: string) => {
    const bdTime = toBangladeshTime(dateStr);
    return bdTime.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getHeadlinePreview = (headline: string, maxLength: number = 60) => {
    if (headline.length <= maxLength) return headline;
    return headline.substring(0, maxLength) + '...';
  };

  const hasHardNews = !!session.hard_news;
  const hasSoftNews = !!session.soft_news;
  const hasBoth = hasHardNews && hasSoftNews;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-4 text-left">
          <div className="flex items-center gap-2">
            {hasHardNews && (
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                Hard
              </span>
            )}
            {hasSoftNews && (
              <span className="px-2 py-0.5 bg-teal-100 text-teal-700 text-xs font-medium rounded-full">
                Soft
              </span>
            )}
          </div>
          <div>
            <p className="font-medium text-gray-900">{getHeadlinePreview(session.headline)}</p>
            <p className="text-sm text-gray-500">{formatTime(session.created_at)}</p>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <HiChevronDown className="w-5 h-5 text-gray-400" />
        </motion.div>
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-2 border-t border-gray-100">
              {/* Format Boxes - Side by Side if both exist, Full width if only one */}
              <div className={`flex gap-4 ${hasBoth ? 'flex-col sm:flex-row' : 'flex-col'}`}>
                {hasHardNews && session.hard_news && (
                  <FormatBox
                    title="হার্ড নিউজ"
                    formatType="hard_news"
                    data={session.hard_news}
                    englishContent={session.english_content}
                    fullWidth={!hasBoth}
                  />
                )}
                {hasSoftNews && session.soft_news && (
                  <FormatBox
                    title="সফট নিউজ"
                    formatType="soft_news"
                    data={session.soft_news}
                    englishContent={session.english_content}
                    fullWidth={!hasBoth}
                  />
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default EnhancementSessionCard;
