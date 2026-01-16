/**
 * News Generator Page - Generate Bengali news articles from English content
 * State persists across tab changes via Zustand store
 */

import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { useTranslate } from '../hooks/useTranslation';
import { ContextBar } from '../components/translation/ContextBar';
import { PasteArea } from '../components/translation/PasteArea';
import { ContentPreview } from '../components/translation/ContentPreview';
import { EnhancementSection } from '../components/translation/EnhancementSection';
import toast from 'react-hot-toast';

export const TranslationPage = () => {
  const navigate = useNavigate();
  const {
    selectedArticle,
    selectArticle,
    pastedContent,
    setPastedContent,
    currentTranslation,
    setCurrentTranslation,
    clearTranslationState,
  } = useAppStore();
  const translate = useTranslate();

  const handleClearSelection = () => {
    selectArticle(null);
  };

  const handleClearAll = () => {
    clearTranslationState();
    toast.success('Cleared all data');
  };

  const handleTranslate = async () => {
    if (!pastedContent.trim()) {
      toast.error('Please paste article content first');
      return;
    }

    try {
      const result = await translate.mutateAsync(pastedContent);
      // Store in global state so it persists across tab changes
      setCurrentTranslation({
        original: pastedContent,
        translated: result.translated_text,
        tokens_used: result.tokens_used,
        timestamp: new Date().toISOString(),
      });
      toast.success('Content processed!');
    } catch (error: any) {
      // Error already handled by useTranslate hook
      console.error('Translation error:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ✨ News Generator
        </h1>
        <p className="text-gray-600">
          {selectedArticle
            ? 'Generate Bengali news articles from your selected content'
            : 'Paste any English content to generate Bengali news articles'
          }
        </p>
      </div>

      {/* Context Bar - Shows selected article OR manual mode indicator */}
      {selectedArticle ? (
        <ContextBar article={selectedArticle} onClear={handleClearSelection} />
      ) : (
        <div className="mb-6 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-4 border-2 border-purple-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">✍️</span>
              <div>
                <h3 className="font-semibold text-purple-900">Manual Mode</h3>
                <p className="text-sm text-purple-700">
                  Paste any content from anywhere - no article selection needed
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/articles')}
              className="px-4 py-2 text-purple-700 hover:bg-purple-100 rounded-lg text-sm font-medium transition-colors"
            >
              Or select from articles →
            </button>
          </div>
        </div>
      )}

      {/* Paste Area */}
      <PasteArea
        value={pastedContent}
        onChange={setPastedContent}
        onTranslate={handleTranslate}
        isLoading={translate.isPending}
      />

      {/* Content Preview - Shows English content after translation */}
      {currentTranslation && (
        <div className="mt-8">
          <div className="flex justify-end mb-2">
            <button
              onClick={handleClearAll}
              className="text-sm text-red-500 hover:text-red-600 hover:underline"
            >
              Clear All & Start Fresh
            </button>
          </div>
          <ContentPreview content={currentTranslation.original} />
        </div>
      )}

      {/* Enhancement Section */}
      {currentTranslation && (
        <EnhancementSection translatedText={currentTranslation.translated} />
      )}

      {/* Help Section */}
      {!currentTranslation && (
        <div className="mt-8 bg-blue-50 rounded-xl p-6 border-2 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            💡 How to use
          </h3>
          <ol className="space-y-2 text-sm text-blue-800">
            {selectedArticle ? (
              <>
                <li className="flex items-start gap-2">
                  <span className="font-bold">1.</span>
                  <span>Open the article URL (click the 🔗 link in the context bar above)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold">2.</span>
                  <span>Copy the entire webpage content (Ctrl+A, Ctrl+C)</span>
                </li>
              </>
            ) : (
              <>
                <li className="flex items-start gap-2">
                  <span className="font-bold">1.</span>
                  <span>Copy any travel news content from any website or document</span>
                </li>
              </>
            )}
            <li className="flex items-start gap-2">
              <span className="font-bold">{selectedArticle ? '3.' : '2.'}</span>
              <span>Paste the content in the text area above and click "Process Content"</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">{selectedArticle ? '4.' : '3.'}</span>
              <span>Select <strong>Hard News</strong> or <strong>Soft News</strong> format and generate</span>
            </li>
          </ol>

          {/* Prompts Info */}
          <div className="mt-4 pt-4 border-t border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-2">📝 Output Formats</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="bg-white/50 rounded-lg p-3">
                <span className="font-bold">📄 Hard News:</span> Professional, factual, 300-500 words, inverted pyramid
              </div>
              <div className="bg-white/50 rounded-lg p-3">
                <span className="font-bold">✍️ Soft News:</span> Literary, storytelling, 500-800 words, emotional
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Back to Articles Button */}
      <div className="mt-8 flex justify-center">
        <button
          onClick={() => navigate('/articles')}
          className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold transition-colors"
        >
          ← Back to Articles
        </button>
      </div>
    </div>
  );
};
