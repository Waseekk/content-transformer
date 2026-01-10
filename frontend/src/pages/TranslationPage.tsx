/**
 * Translation Page - Translate and enhance selected articles
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { useTranslate } from '../hooks/useTranslation';
import { ContextBar } from '../components/translation/ContextBar';
import { PasteArea } from '../components/translation/PasteArea';
import { TranslationResult } from '../components/translation/TranslationResult';
import { EnhancementSection } from '../components/translation/EnhancementSection';
import toast from 'react-hot-toast';

export const TranslationPage = () => {
  const navigate = useNavigate();
  const { selectedArticle, selectArticle } = useAppStore();
  const translate = useTranslate();

  const [pastedContent, setPastedContent] = useState('');
  const [translationData, setTranslationData] = useState<any>(null);

  const handleClearSelection = () => {
    selectArticle(null);
  };

  const handleTranslate = async () => {
    if (!pastedContent.trim()) {
      toast.error('Please paste article content first');
      return;
    }

    try {
      const result = await translate.mutateAsync(pastedContent);
      setTranslationData(result);
      toast.success('Translation completed!');
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
          🌐 Translate & Enhance
        </h1>
        <p className="text-gray-600">
          {selectedArticle
            ? 'Translate your selected article and generate multiple content formats'
            : 'Paste any content to translate and generate multiple formats'
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

      {/* Translation Result */}
      {translationData && (
        <div className="mt-8">
          <TranslationResult
            original={translationData.original_text || pastedContent}
            translated={translationData.translated_text}
            tokensUsed={translationData.tokens_used}
            extractedData={{
              headline: translationData.headline,
              content: translationData.content,
              author: translationData.author,
              published_date: translationData.published_date,
            }}
          />
        </div>
      )}

      {/* Enhancement Section */}
      {translationData && (
        <EnhancementSection translatedText={translationData.translated_text} />
      )}

      {/* Help Section */}
      {!translationData && (
        <div className="mt-8 bg-blue-50 rounded-xl p-6 border-2 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            💡 How to use this page
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
                  <span>Copy any travel news content from any website, document, or source</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-bold">2.</span>
                  <span>You can also paste raw text, HTML, or full webpage content</span>
                </li>
              </>
            )}
            <li className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <span>Paste the content in the text area above - AI will extract and translate automatically</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">4.</span>
              <span>After translation, generate <strong>Hard News</strong> or <strong>Soft News</strong> formats</span>
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
