/**
 * Translation Page - Translate and enhance selected articles
 */

import React, { useState, useEffect } from 'react';
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
  const { selectedArticle, selectArticle, currentTranslation } = useAppStore();
  const translate = useTranslate();

  const [pastedContent, setPastedContent] = useState('');
  const [translationData, setTranslationData] = useState<any>(null);

  // Redirect if no article selected
  useEffect(() => {
    if (!selectedArticle) {
      toast.error('Please select an article first');
      navigate('/articles');
    }
  }, [selectedArticle, navigate]);

  const handleClearSelection = () => {
    selectArticle(null);
    navigate('/articles');
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

  if (!selectedArticle) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🌐 Translate & Enhance
        </h1>
        <p className="text-gray-600">
          Translate your selected article and generate multiple content formats
        </p>
      </div>

      {/* Context Bar - Shows selected article */}
      <ContextBar article={selectedArticle} onClear={handleClearSelection} />

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
            <li className="flex items-start gap-2">
              <span className="font-bold">1.</span>
              <span>
                Open the article URL (click the 🔗 link in the context bar above)
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">2.</span>
              <span>
                Copy the entire webpage content (Ctrl+A, Ctrl+C or use "View Page Source")
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <span>
                Paste the content in the text area above - our AI will automatically extract and translate the article
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">4.</span>
              <span>
                After translation, select formats to generate enhanced content variations
              </span>
            </li>
          </ol>
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
