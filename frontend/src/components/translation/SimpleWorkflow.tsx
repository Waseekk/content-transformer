/**
 * SimpleWorkflow Component
 * Streamlined workflow for single-format clients
 * URL/paste -> Process -> Result (no content preview, no format selection)
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslate } from '../../hooks/useTranslation';
import { useEnhance } from '../../hooks/useEnhancement';
import toast from 'react-hot-toast';
import { AILoader, GlowButton, AnimatedCard } from '../ui';
import { FormatCard } from './FormatCard';
import { URLExtractor } from './URLExtractor';
import type { UserFormatConfig } from '../../types/auth';
import { useAppStore } from '../../store/useAppStore';
import { isBijoyEncoded, convertBijoyToUnicode } from '../../utils/bijoyToUnicode';
import {
  HiSparkles,
  HiLightningBolt,
  HiClipboard,
  HiTrash,
  HiNewspaper,
  HiBookOpen,
  HiDocumentText,
} from 'react-icons/hi';

interface SimpleWorkflowProps {
  defaultFormat: UserFormatConfig;
  appTitle?: string;
}

// Icon mapping
const iconMap: Record<string, typeof HiNewspaper> = {
  newspaper: HiNewspaper,
  book: HiBookOpen,
  sparkles: HiSparkles,
  document: HiDocumentText,
};

export const SimpleWorkflow: React.FC<SimpleWorkflowProps> = ({
  defaultFormat,
  appTitle = 'AI Content Assistant',
}) => {
  const translate = useTranslate();
  const enhance = useEnhance();

  const [pastedContent, setPastedContent] = useState('');

  const {
    simpleWorkflowResult: result,
    simpleWorkflowTranslation: translation,
    simpleWorkflowProcessing: isProcessing,
    setSimpleWorkflowResult,
    setSimpleWorkflowTranslation,
    setSimpleWorkflowProcessing,
    clearSimpleWorkflow,
  } = useAppStore();

  const handleClearAll = () => {
    setPastedContent('');
    clearSimpleWorkflow();
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const pasted = e.clipboardData.getData('text');
    if (isBijoyEncoded(pasted)) {
      e.preventDefault();
      const converted = convertBijoyToUnicode(pasted);
      setPastedContent(converted);
      toast.success('Bijoy text detected — converted to Unicode automatically');
    }
    // else: let browser handle paste normally
  };

  const handleProcess = async () => {
    if (!pastedContent.trim()) {
      toast.error('Please paste content first');
      return;
    }

    setSimpleWorkflowProcessing(true);
    setSimpleWorkflowResult(null);

    try {
      // Step 1: Translate/process content
      const translateResult = await translate.mutateAsync({
        text: pastedContent,
        inputLanguage: 'auto',
      });

      setSimpleWorkflowTranslation({
        original: translateResult.original_text,
        translated: translateResult.translated_text,
      });

      // Step 2: Generate with default format
      const enhanceResult = await enhance.mutateAsync({
        text: translateResult.translated_text,
        headline: 'Content',
        formats: [defaultFormat.slug],
      });

      if (enhanceResult.formats && enhanceResult.formats.length > 0) {
        setSimpleWorkflowResult({
          content: enhanceResult.formats[0].content,
          tokens_used: enhanceResult.formats[0].tokens_used,
        });
      }
    } catch (error: any) {
      const httpStatus = error?.response?.status;
      if (httpStatus === 504) {
        toast.error('Request timed out. The content may be too long or the server is busy. Please try again.');
      } else {
        toast.error(error?.response?.data?.detail || error.message || 'Processing failed');
      }
    } finally {
      setSimpleWorkflowProcessing(false);
    }
  };

  const handleURLExtracted = (englishContent: string, bengaliContent: string, _title?: string) => {
    // Set translation and auto-process
    setSimpleWorkflowTranslation({
      original: englishContent,
      translated: bengaliContent,
    });
    setPastedContent('');

    // Auto-generate with default format
    setSimpleWorkflowProcessing(true);
    setSimpleWorkflowResult(null);

    enhance.mutateAsync({
      text: bengaliContent,
      headline: 'Content',
      formats: [defaultFormat.slug],
    })
      .then((enhanceResult) => {
        if (enhanceResult.formats && enhanceResult.formats.length > 0) {
          setSimpleWorkflowResult({
            content: enhanceResult.formats[0].content,
            tokens_used: enhanceResult.formats[0].tokens_used,
          });
        }
      })
      .catch((error) => {
        const httpStatus = error?.response?.status;
        if (httpStatus === 504) {
          toast.error('Extraction timed out. Please try a different URL or paste the content directly.');
        } else {
          toast.error(error?.response?.data?.detail || error.message || 'Processing failed');
        }
      })
      .finally(() => {
        setSimpleWorkflowProcessing(false);
      });
  };

  const handleContentUpdate = (_formatId: string, newContent: string) => {
    if (result) {
      setSimpleWorkflowResult({ ...result, content: newContent });
    }
  };

  const Icon = iconMap[defaultFormat.icon] || HiDocumentText;
  const wordCount = pastedContent.split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen ai-gradient-bg">
      <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
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
            {appTitle}
          </h1>
          <p className="text-gray-500 text-lg">
            AI Powered Clean and Credible News
          </p>
        </motion.div>

        {/* URL Extractor */}
        <URLExtractor onExtractedAndTranslated={handleURLExtracted} />

        {/* Paste Area (when no result yet) */}
        {!result && (
          <AnimatedCard delay={0.1} className="mb-6 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-ai-primary/10 rounded-xl flex items-center justify-center">
                  <HiClipboard className="w-5 h-5 text-ai-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Paste Content</h3>
                  <p className={`text-sm ${wordCount > 1500 ? 'text-amber-500 font-medium' : 'text-gray-500'}`}>
                    {wordCount > 0 ? `${wordCount} words${wordCount > 1500 ? ' — long content may timeout, try a shorter extract' : ''}` : 'Or use URL above'}
                  </p>
                </div>
              </div>
            </div>

            <textarea
              value={pastedContent}
              onChange={(e) => setPastedContent(e.target.value)}
              onPaste={handlePaste}
              placeholder="Paste your content here...

The AI will automatically process and generate content."
              className="textarea-premium min-h-[200px] mb-4"
            />

            <div className="flex items-center justify-end">
              <GlowButton
                onClick={handleProcess}
                disabled={!pastedContent.trim() || isProcessing}
                loading={isProcessing}
                icon={<HiLightningBolt className="w-5 h-5" />}
              >
                {isProcessing ? 'Processing...' : 'Process & Generate'}
              </GlowButton>
            </div>
          </AnimatedCard>
        )}

        {/* Processing State */}
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center py-12"
          >
            <AILoader variant="neural" size="lg" text="Generating content..." />
          </motion.div>
        )}

        {/* Result */}
        <AnimatePresence>
          {result && !isProcessing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <FormatCard
                formatId={defaultFormat.slug}
                title={defaultFormat.display_name}
                subtitle={defaultFormat.description || ''}
                icon={Icon}
                description=""
                content={result.content}
                englishContent={translation?.original || ''}
                isLoading={false}
                color="blue"
                onContentUpdate={handleContentUpdate}
              />

              {/* Clear Button */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-10 flex justify-center"
              >
                <button
                  onClick={handleClearAll}
                  className="inline-flex items-center gap-2 px-5 py-2.5 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl font-medium transition-all"
                >
                  <HiTrash className="w-4 h-4" />
                  Clear & Start Fresh
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
