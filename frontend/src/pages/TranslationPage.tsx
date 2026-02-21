/**
 * AI Assistant Page - Premium Design
 * Generate Bengali news articles with AI-powered translation
 *
 * Supports adaptive UI based on user's client configuration:
 * - Full workflow: Content preview, format selection (default)
 * - Simple workflow: Direct processing with default format
 */

import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { useTranslate } from '../hooks/useTranslation';
import { useEnhance } from '../hooks/useEnhancement';
import { useNavigationWarning } from '../hooks/useNavigationWarning';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { AILoader, GlowButton, AnimatedCard } from '../components/ui';
import { FormatCard } from '../components/translation/FormatCard';
import { URLExtractor } from '../components/translation/URLExtractor';
import { SimpleWorkflow } from '../components/translation/SimpleWorkflow';
import {
  HiSparkles,
  HiPencilAlt,
  HiArrowRight,
  HiTrash,
  HiLightningBolt,
  HiDocumentText,
  HiNewspaper,
  HiBookOpen,
  HiCheckCircle,
  HiChevronDown,
  HiClipboard,
  HiClipboardCheck,
  HiExternalLink,
} from 'react-icons/hi';
import { useState, useEffect, useMemo } from 'react';
import { detectLanguage, getLanguageInfo } from '../utils/languageDetection';

export const TranslationPage = () => {
  const navigate = useNavigate();
  const { userConfig } = useAuth();

  // All hooks must be called before any conditional returns (React rules of hooks)
  const {
    selectedArticle,
    selectArticle,
    pastedContent,
    setPastedContent,
    currentTranslation,
    setCurrentTranslation,
    clearTranslationState,
    selectedFormats,
    toggleFormat,
    currentEnhancements,
    addEnhancement,
    clearEnhancementState,
    startOperation,
    completeOperation,
    failOperation,
    pendingOperations,
    markOperationApplied,
    clearOperation,
  } = useAppStore();
  const translate = useTranslate();
  const enhance = useEnhance();
  const [showEnglish, setShowEnglish] = useState(false);
  const [translationSource, setTranslationSource] = useState<'url' | 'paste' | null>(null);
  const [languageOverride, _setLanguageOverride] = useState<'auto' | 'en' | 'bn'>('auto');
  const [urlCopied, setUrlCopied] = useState(false);

  // Auto-detect language from pasted content
  const detectedLanguage = useMemo(() => {
    if (!pastedContent || pastedContent.trim().length < 20) return null;
    return detectLanguage(pastedContent);
  }, [pastedContent]);

  // Warn user when navigating away with pending operations
  useNavigationWarning();

  // Apply unapplied completed operations when returning to this page
  useEffect(() => {
    // Skip in simple workflow mode — SimpleWorkflow handles its own state
    if ((userConfig?.ui_settings?.workflow_type || 'full') === 'simple') return;

    const unappliedOps = Object.values(pendingOperations).filter(
      (op: { status: string; applied?: boolean }) => op.status === 'completed' && !op.applied
    );

    unappliedOps.forEach((op: any) => {
      if (op.type === 'enhancement' && op.result?.formats) {
        // Apply enhancement results
        op.result.formats.forEach((result: any) => {
          addEnhancement(result.format_type, {
            format_type: result.format_type,
            content: result.content,
            tokens_used: result.tokens_used,
            timestamp: new Date().toISOString(),
          });
        });
        toast.success('News articles generated while you were away!');
      } else if (op.type === 'translation' && op.result) {
        // Apply translation results
        setCurrentTranslation({
          original: op.result.original_text,
          translated: op.result.translated_text,
          tokens_used: op.result.tokens_used,
          timestamp: new Date().toISOString(),
        });
        setTranslationSource('paste');
        toast.success('Content processed while you were away!');
      } else if (op.type === 'url_extraction' && op.result) {
        // Apply URL extraction results
        if (op.result.english_content && op.result.bengali_content) {
          setCurrentTranslation({
            original: op.result.english_content,
            translated: op.result.bengali_content,
            tokens_used: 0,
            timestamp: new Date().toISOString(),
          });
          setTranslationSource('url');
          setShowEnglish(true);
          toast.success('URL extracted & translated while you were away!');
        }
      }

      // Mark as applied and clear after a delay
      markOperationApplied(op.id);
      setTimeout(() => clearOperation(op.id), 5000);
    });
  }, [pendingOperations]);

  // Check for simple workflow mode (after all hooks)
  const workflowType = userConfig?.ui_settings?.workflow_type || 'full';
  const appTitle = userConfig?.ui_settings?.app_title || 'AI Assistant';

  // If simple workflow and has default format, render SimpleWorkflow
  if (workflowType === 'simple' && userConfig?.default_format) {
    return (
      <SimpleWorkflow
        defaultFormat={userConfig.default_format}
        appTitle={appTitle}
      />
    );
  }

  const handleClearSelection = () => {
    selectArticle(null);
  };

  const handleCopyUrl = async () => {
    if (selectedArticle?.article_url) {
      try {
        await navigator.clipboard.writeText(selectedArticle.article_url);
        setUrlCopied(true);
        toast.success('URL copied!');
        setTimeout(() => setUrlCopied(false), 2000);
      } catch {
        toast.error('Failed to copy URL');
      }
    }
  };

  const handleClearAll = () => {
    clearTranslationState();
    setTranslationSource(null);
    toast.success('Cleared all data');
  };

  const handleTranslate = async () => {
    if (!pastedContent.trim()) {
      toast.error('Please paste article content first');
      return;
    }

    // Clear previous enhancements (hard news, soft news) when processing new content
    clearEnhancementState();

    const operationId = `translate_${Date.now()}`;
    startOperation(operationId, 'translation');

    // Determine language to use
    const inputLang = languageOverride !== 'auto' ? languageOverride : 'auto';

    try {
      const result = await translate.mutateAsync({
        text: pastedContent,
        inputLanguage: inputLang,
      });
      setCurrentTranslation({
        original: result.original_text,
        translated: result.translated_text,
        tokens_used: result.tokens_used,
        timestamp: new Date().toISOString(),
      });
      setTranslationSource('paste');
      completeOperation(operationId, result);

      // Show appropriate message based on language
      if (result.extraction_method === 'bengali_passthrough') {
        toast.success('Bengali content ready! Select format to generate news.');
      } else {
        toast.success('Content processed!');
      }
    } catch (error: any) {
      failOperation(operationId, error.message || 'Translation failed');
    }
  };

  const handleEnhance = async () => {
    if (selectedFormats.length === 0) return;

    const operationId = `enhance_${Date.now()}`;
    startOperation(operationId, 'enhancement', selectedFormats);

    try {
      const response = await enhance.mutateAsync({
        text: currentTranslation?.translated || '',
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

      completeOperation(operationId, response);
      toast.success('News articles generated!');
    } catch (error: any) {
      failOperation(operationId, error.message || 'Enhancement failed');
    }
  };

  const handleContentUpdate = (formatId: string, newContent: string) => {
    const existing = currentEnhancements[formatId];
    if (existing) {
      addEnhancement(formatId, { ...existing, content: newContent });
    }
  };

  const handleURLExtractedAndTranslated = (englishContent: string, bengaliContent: string, _title?: string, extractionMethod?: string) => {
    // Clear previous enhancements and paste content
    clearEnhancementState();
    setPastedContent(''); // Clear paste area - URL extraction doesn't use it

    // Check if it was Bengali passthrough
    const isBengaliPassthrough = extractionMethod?.includes('bengali_passthrough') || false;

    // Set the current translation directly (skip "Process Content" step)
    setCurrentTranslation({
      original: englishContent,
      translated: bengaliContent,
      tokens_used: 0, // Token info is in the API response, but we don't need it here
      timestamp: new Date().toISOString(),
    });

    // Mark that translation came from URL
    setTranslationSource('url');

    // Auto-expand the extracted content section for URL extractions
    setShowEnglish(true);

    // Show appropriate message
    if (isBengaliPassthrough) {
      toast.success('Bengali content ready! Select format to generate news.');
    } else {
      toast.success('Extracted & translated! Select format to generate news.');
    }
  };

  // Icon mapping for dynamic formats
  const iconMap: Record<string, typeof HiNewspaper> = {
    newspaper: HiNewspaper,
    book: HiBookOpen,
    sparkles: HiSparkles,
    document: HiDocumentText,
  };

  // Format definitions - use user's config if available, otherwise defaults
  const formats = useMemo(() => {
    if (userConfig?.formats && userConfig.formats.length > 0) {
      return userConfig.formats.map((f, index) => ({
        id: f.slug,
        title: f.display_name,
        subtitle: f.display_name, // Bengali subtitle
        icon: iconMap[f.icon] || HiDocumentText,
        description: f.description || '',
        color: index % 2 === 0 ? 'blue' : 'purple',
      }));
    }

    // Default formats
    return [
      {
        id: 'hard_news',
        title: 'Hard News',
        subtitle: 'হার্ড নিউজ',
        icon: HiNewspaper,
        description: 'Professional factual reporting',
        color: 'blue',
      },
      {
        id: 'soft_news',
        title: 'Soft News',
        subtitle: 'সফট নিউজ',
        icon: HiBookOpen,
        description: 'Literary travel feature',
        color: 'purple',
      },
    ];
  }, [userConfig?.formats]);

  const wordCount = pastedContent.split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen ai-gradient-bg">
      <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-2xl bg-gradient-to-br from-ai-primary to-ai-secondary ai-sparkle-box"
          >
            <HiSparkles className="w-8 h-8 text-white ai-sparkle-icon" />
          </motion.div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI <span className="ai-header-gradient ai-header-sparkle">Assistant</span>
          </h1>
          <p className="text-gray-500 text-lg">
            Transform English content into professional Bengali news articles
          </p>
        </motion.div>

        {/* Context Bar */}
        <AnimatedCard delay={0.1} className="mb-6 p-5">
          {selectedArticle ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 flex-1 min-w-0">
                {/* Modern gradient indicator */}
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  className="relative flex-shrink-0"
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                    <HiDocumentText className="w-6 h-6 text-white" />
                  </div>
                  {/* Active indicator dot */}
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full border-2 border-white shadow-sm"
                  />
                </motion.div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium px-2 py-0.5 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 rounded-full">
                      {selectedArticle.publisher}
                    </span>
                    <span className="text-xs text-gray-400">Selected Article</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 line-clamp-1 flex-1">
                      {selectedArticle.headline}
                    </h3>
                    {/* Copy URL and External link icons */}
                    {selectedArticle.article_url && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopyUrl();
                          }}
                          className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-100 hover:bg-emerald-100 flex items-center justify-center transition-colors group"
                          title="Copy URL"
                        >
                          {urlCopied ? (
                            <HiClipboardCheck className="w-4 h-4 text-emerald-500" />
                          ) : (
                            <HiClipboard className="w-4 h-4 text-gray-500 group-hover:text-emerald-600 transition-colors" />
                          )}
                        </button>
                        <a
                          href={selectedArticle.article_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-100 hover:bg-indigo-100 flex items-center justify-center transition-colors group"
                          title="Open original article"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <HiExternalLink className="w-4 h-4 text-gray-500 group-hover:text-indigo-600 transition-colors" />
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={handleClearSelection}
                className="flex-shrink-0 ml-3 text-gray-400 hover:text-red-500 transition-colors p-2 hover:bg-red-50 rounded-lg"
                title="Clear selection"
              >
                <HiTrash className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <motion.div
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-12 h-12 bg-gradient-to-br from-ai-primary to-ai-secondary rounded-xl flex items-center justify-center"
                >
                  <HiPencilAlt className="w-6 h-6 text-white" />
                </motion.div>
                <div>
                  <h3 className="font-semibold text-gray-900">Manual Mode</h3>
                  <p className="text-sm text-gray-500">
                    Paste any content from anywhere
                  </p>
                </div>
              </div>
              <GlowButton
                variant="ghost"
                size="sm"
                onClick={() => navigate('/articles')}
                icon={<HiArrowRight className="w-4 h-4" />}
              >
                Select from articles
              </GlowButton>
            </div>
          )}
        </AnimatedCard>

        {/* URL Extractor - Extract & Translate in one step */}
        <URLExtractor onExtractedAndTranslated={handleURLExtractedAndTranslated} />

        {/* Paste Area - Hide when translation came from URL */}
        {translationSource !== 'url' && (
          <AnimatedCard delay={0.2} className="mb-6 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-ai-primary/10 rounded-xl flex items-center justify-center">
                  <HiClipboard className="w-5 h-5 text-ai-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Content Extraction</h3>
                  <p className="text-sm text-gray-500">
                    {wordCount > 0 ? `${wordCount} words` : 'Paste article content (English or Bengali)'}
                  </p>
                </div>
              </div>
              {/* Language Detection Badge */}
              {detectedLanguage && wordCount > 10 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${
                    detectedLanguage === 'bn'
                      ? 'bg-emerald-100 text-emerald-700'
                      : detectedLanguage === 'en'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  <span>{getLanguageInfo(detectedLanguage).flag}</span>
                  <span>{getLanguageInfo(detectedLanguage).name}</span>
                </motion.div>
              )}
            </div>

            <textarea
              value={pastedContent}
              onChange={(e) => setPastedContent(e.target.value)}
              placeholder="Paste your article content here...

The AI will automatically:
• Detect language (English or Bengali)
• Extract clean article text from web pages
• Remove navigation, ads, and irrelevant content
• Translate to Bangladeshi Bengali (if English)"
              className="textarea-premium min-h-[200px] mb-4"
            />

            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-400">
                Supports: English & Bengali articles, news, blog posts
              </p>
              <GlowButton
                onClick={handleTranslate}
                disabled={!pastedContent.trim()}
                loading={translate.isPending}
                icon={<HiLightningBolt className="w-5 h-5" />}
              >
                {translate.isPending
                  ? 'Processing...'
                  : detectedLanguage === 'bn'
                    ? 'Process Bengali Content'
                    : 'Process Content'}
              </GlowButton>
            </div>
          </AnimatedCard>
        )}

        {/* Content Ready Section */}
        <AnimatePresence mode="wait">
          {currentTranslation && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              {/* Extracted Content Preview (Collapsible) */}
              <AnimatedCard delay={0.1} className="mb-6 overflow-hidden">
                <button
                  onClick={() => setShowEnglish(!showEnglish)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      translationSource === 'url' ? 'bg-emerald-100' : 'bg-blue-100'
                    }`}>
                      <HiDocumentText className={`w-5 h-5 ${
                        translationSource === 'url' ? 'text-emerald-600' : 'text-blue-600'
                      }`} />
                    </div>
                    <div className="text-left">
                      <h4 className="font-semibold text-gray-900">
                        {translationSource === 'url' ? 'Extracted Content' : 'English Content'}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {currentTranslation.original.split(/\s+/).filter(Boolean).length} words
                        {translationSource === 'url' && ' • From URL'}
                        {' • Click to '}{showEnglish ? 'collapse' : 'expand'}
                      </p>
                    </div>
                  </div>
                  <motion.div
                    animate={{ rotate: showEnglish ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center"
                  >
                    <HiChevronDown className="w-5 h-5 text-gray-500" />
                  </motion.div>
                </button>

                <AnimatePresence>
                  {showEnglish && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 border-t border-gray-100">
                        <div className="mt-4 p-4 bg-gray-50 rounded-xl max-h-64 overflow-y-auto">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                            {currentTranslation.original}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </AnimatedCard>

              {/* AI Generation Section */}
              <AnimatedCard delay={0.2} variant="glow" className="mb-6 p-6">
                <div className="flex items-center gap-3 mb-6">
                  <motion.div
                    animate={{
                      boxShadow: [
                        '0 0 20px rgba(99, 102, 241, 0.3)',
                        '0 0 40px rgba(99, 102, 241, 0.5)',
                        '0 0 20px rgba(99, 102, 241, 0.3)',
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-12 h-12 bg-gradient-to-br from-ai-primary to-ai-secondary rounded-xl flex items-center justify-center"
                  >
                    <HiSparkles className="w-6 h-6 text-white" />
                  </motion.div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      Generate News Articles
                    </h3>
                    <p className="text-sm text-gray-500">
                      Select format(s) and let Swiftor create professional Bengali news
                    </p>
                  </div>
                </div>

                {/* Format Selection */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  {formats.map((format, index) => {
                    const isSelected = selectedFormats.includes(format.id);
                    const Icon = format.icon;

                    return (
                      <motion.button
                        key={format.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => toggleFormat(format.id)}
                        className={`
                          format-card text-left
                          ${isSelected ? 'format-card-selected' : 'format-card-unselected'}
                        `}
                      >
                        <div className="flex items-start gap-4">
                          <div className={`
                            w-12 h-12 rounded-xl flex items-center justify-center transition-all
                            ${isSelected
                              ? 'bg-gradient-to-br from-ai-primary to-ai-secondary shadow-glow-sm'
                              : format.color === 'blue'
                                ? 'bg-blue-100'
                                : 'bg-purple-100'
                            }
                          `}>
                            <Icon className={`w-6 h-6 ${isSelected ? 'text-white' : format.color === 'blue' ? 'text-blue-600' : 'text-purple-600'}`} />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className="font-bold text-gray-900">{format.title}</h4>
                              {isSelected && (
                                <motion.div
                                  initial={{ scale: 0 }}
                                  animate={{ scale: 1 }}
                                  className="w-5 h-5 rounded-full bg-ai-primary flex items-center justify-center"
                                >
                                  <HiCheckCircle className="w-4 h-4 text-white" />
                                </motion.div>
                              )}
                            </div>
                            <p className="text-sm text-ai-primary font-medium">{format.subtitle}</p>
                            <p className="text-sm text-gray-500 mt-1">{format.description}</p>
                          </div>
                        </div>
                      </motion.button>
                    );
                  })}
                </div>

                {/* Generate Button */}
                <div className="flex justify-center">
                  <GlowButton
                    onClick={handleEnhance}
                    disabled={selectedFormats.length === 0}
                    loading={enhance.isPending}
                    size="lg"
                    icon={<HiSparkles className="w-5 h-5" />}
                  >
                    {enhance.isPending ? (
                      'Swiftor is generating...'
                    ) : (
                      <>Generate {selectedFormats.length > 0 ? `(${selectedFormats.length} format${selectedFormats.length > 1 ? 's' : ''})` : ''}</>
                    )}
                  </GlowButton>
                </div>

                {/* AI Processing State */}
                {enhance.isPending && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-8 flex flex-col items-center"
                  >
                    <AILoader variant="neural" size="lg" text="Swiftor is crafting your news articles..." />
                  </motion.div>
                )}
              </AnimatedCard>

              {/* Generated Results */}
              <AnimatePresence>
                {selectedFormats.length > 0 && !enhance.isPending && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-6"
                  >
                    {selectedFormats.map((formatId: string, index: number) => {
                      const format = formats.find((f) => f.id === formatId);
                      if (!format) return null;

                      const result = currentEnhancements[formatId];
                      const Icon = format.icon;

                      return (
                        <motion.div
                          key={formatId}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.15 }}
                        >
                          <FormatCard
                            formatId={formatId}
                            title={format.subtitle}
                            subtitle="বাংলার কলম্বাস"
                            icon={Icon}
                            description={format.description}
                            content={result?.content}
                            englishContent={currentTranslation.original}
                            isLoading={enhance.isPending && !result}
                            color={format.color === 'blue' ? 'blue' : 'teal'}
                            onContentUpdate={handleContentUpdate}
                          />
                        </motion.div>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Clear Button */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-10 flex justify-center"
              >
                <button
                  onClick={handleClearAll}
                  className="inline-flex items-center gap-2 px-5 py-2.5 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl font-medium transition-all"
                >
                  <HiTrash className="w-4 h-4" />
                  Clear All & Start Fresh
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Help Section (shown when no content) */}
        {!currentTranslation && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <AnimatedCard delay={0.3} className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-ai-primary/10 rounded-xl flex items-center justify-center">
                  <HiLightningBolt className="w-5 h-5 text-ai-primary" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">
                  How it works
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    step: '01',
                    title: 'Content Extraction',
                    desc: 'Copy any English news article and paste it above',
                    icon: HiClipboard,
                  },
                  {
                    step: '02',
                    title: 'AI Processing',
                    desc: 'Our AI extracts and translates the content',
                    icon: HiSparkles,
                  },
                  {
                    step: '03',
                    title: 'Generate News',
                    desc: 'Choose format and get professional Bengali articles',
                    icon: HiNewspaper,
                  },
                ].map((item, index) => (
                  <motion.div
                    key={item.step}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="relative"
                  >
                    <div className="text-5xl font-bold text-ai-primary/10 absolute -top-2 -left-2">
                      {item.step}
                    </div>
                    <div className="relative pt-6">
                      <div className="w-10 h-10 bg-ai-primary/10 rounded-xl flex items-center justify-center mb-3">
                        <item.icon className="w-5 h-5 text-ai-primary" />
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-1">{item.title}</h4>
                      <p className="text-sm text-gray-500">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Output Formats Preview */}
              <div className="mt-8 pt-6 border-t border-gray-100">
                <h4 className="font-semibold text-gray-900 mb-4">Output Formats</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {formats.map((format, index) => {
                    const Icon = format.icon;
                    return (
                      <motion.div
                        key={format.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + index * 0.1 }}
                        className="bg-gray-50 rounded-xl p-4 border border-gray-100"
                      >
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            format.color === 'blue' ? 'bg-blue-100' : 'bg-purple-100'
                          }`}>
                            <Icon className={`w-4 h-4 ${
                              format.color === 'blue' ? 'text-blue-600' : 'text-purple-600'
                            }`} />
                          </div>
                          <div>
                            <span className="font-semibold text-gray-900">{format.title}</span>
                            <span className="text-ai-primary ml-2 text-sm">{format.subtitle}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">{format.description}</p>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </AnimatedCard>
          </motion.div>
        )}

        {/* Back to Articles Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 flex justify-center"
        >
          <button
            onClick={() => navigate('/articles')}
            className="btn-premium inline-flex items-center gap-2"
          >
            <HiArrowRight className="w-5 h-5 rotate-180" />
            Back to Articles
          </button>
        </motion.div>
      </div>
    </div>
  );
};
