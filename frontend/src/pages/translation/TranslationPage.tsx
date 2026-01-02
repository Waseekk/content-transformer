import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Textarea, Card, Badge } from '../../components/common';
import { extractAndTranslate, translateText } from '../../api/translation';
import { enhanceText } from '../../api/enhancement';
import toast from 'react-hot-toast';

export function TranslationPage() {
  const navigate = useNavigate();

  // Translation state
  const [mode, setMode] = useState<'url' | 'text'>('url');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [translation, setTranslation] = useState<any>(null);

  // Enhancement state
  const [enhancementPattern, setEnhancementPattern] = useState<'hard' | 'soft' | 'both'>('both');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancementResults, setEnhancementResults] = useState<any>(null);

  const handleTranslate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTranslating(true);
    setTranslation(null);
    setEnhancementResults(null);

    try {
      let result;
      if (mode === 'url') {
        if (!url.trim()) {
          toast.error('Please enter a URL');
          return;
        }
        result = await extractAndTranslate(url);
        toast.success('Content extracted and translated!');
      } else {
        if (!text.trim()) {
          toast.error('Please enter text to translate');
          return;
        }
        result = await translateText(text);
        toast.success('Text translated successfully!');
      }

      // Map backend response to frontend format
      const mapped = {
        headline: result.original_title || 'Translation',
        content: result.translated_text,
        tokens_used: result.tokens_used,
        id: result.id,
      };

      setTranslation(mapped);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Translation failed';
      toast.error(errorMsg);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleEnhance = async () => {
    if (!translation) {
      toast.error('Please translate content first');
      return;
    }

    setIsEnhancing(true);
    setEnhancementResults(null);

    try {
      // Determine which formats to request based on pattern
      const formats = enhancementPattern === 'hard'
        ? ['hard_news']
        : enhancementPattern === 'soft'
        ? ['soft_news']
        : ['hard_news', 'soft_news'];

      const result = await enhanceText({
        headline: translation.headline,
        text: translation.content,
        formats: formats,
      });

      setEnhancementResults(result);
      toast.success(`Enhanced to ${formats.length} format${formats.length > 1 ? 's' : ''}!`);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Enhancement failed';
      toast.error(errorMsg);
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleClear = () => {
    setUrl('');
    setText('');
    setTranslation(null);
    setEnhancementResults(null);
  };

  const copyToClipboard = (content: string, label: string) => {
    navigator.clipboard.writeText(content);
    toast.success(`${label} copied to clipboard!`);
  };

  const downloadText = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Translation & Enhancement</h1>
            <p className="text-gray-600 mt-2">
              Translate travel news to Bengali and enhance to professional formats
            </p>
          </div>
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>
            ← Dashboard
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {/* SECTION 1: TRANSLATION */}
        <Card title="1. Translate Content" subtitle="Extract and translate travel news to Bengali">
          <div className="mb-4 flex gap-2">
            <Button
              type="button"
              variant={mode === 'url' ? 'primary' : 'secondary'}
              onClick={() => setMode('url')}
              size="sm"
            >
              From URL
            </Button>
            <Button
              type="button"
              variant={mode === 'text' ? 'primary' : 'secondary'}
              onClick={() => setMode('text')}
              size="sm"
            >
              Direct Text
            </Button>
          </div>

          <form onSubmit={handleTranslate} className="space-y-4">
            {mode === 'url' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Article URL
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/travel-article"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isTranslating}
                />
                <p className="mt-1 text-sm text-gray-500">
                  Paste the URL of a travel news article
                </p>
              </div>
            ) : (
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                label="Text to Translate"
                placeholder="Paste the article content here..."
                rows={6}
                disabled={isTranslating}
                helperText="Paste the article text you want to translate to Bengali"
              />
            )}

            <div className="flex gap-3">
              <Button
                type="submit"
                variant="primary"
                isLoading={isTranslating}
                disabled={isTranslating}
              >
                {mode === 'url' ? 'Extract & Translate' : 'Translate'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={handleClear}
                disabled={isTranslating}
              >
                Clear All
              </Button>
            </div>
          </form>
        </Card>

        {/* Translation Result */}
        {translation && (
          <Card title="Translation Result" className="bg-green-50 border border-green-200">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {translation.headline}
                </h3>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{translation.content}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-green-300">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Tokens used:</span> {translation.tokens_used}
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(translation.content, 'Translation')}
                  >
                    Copy
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => downloadText(
                      `${translation.headline}\n\n${translation.content}`,
                      `translation-${Date.now()}.txt`
                    )}
                  >
                    Download
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* SECTION 2: AI ENHANCEMENT (Only show if translation exists) */}
        {translation && (
          <Card
            title="2. AI-Powered Enhancement"
            subtitle="Generate professional news formats"
            className="bg-blue-50 border border-blue-200"
          >
            <div className="space-y-6">
              {/* Pattern Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Choose News Format Pattern
                </label>
                <div className="space-y-3">
                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                    style={{
                      borderColor: enhancementPattern === 'hard' ? '#3b82f6' : '#e5e7eb',
                      backgroundColor: enhancementPattern === 'hard' ? '#eff6ff' : 'white'
                    }}
                  >
                    <input
                      type="radio"
                      name="pattern"
                      value="hard"
                      checked={enhancementPattern === 'hard'}
                      onChange={() => setEnhancementPattern('hard')}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">📰 Hard News Only</div>
                      <div className="text-sm text-gray-600 mt-1">
                        Professional factual reporting - formal news style
                      </div>
                    </div>
                  </label>

                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                    style={{
                      borderColor: enhancementPattern === 'soft' ? '#3b82f6' : '#e5e7eb',
                      backgroundColor: enhancementPattern === 'soft' ? '#eff6ff' : 'white'
                    }}
                  >
                    <input
                      type="radio"
                      name="pattern"
                      value="soft"
                      checked={enhancementPattern === 'soft'}
                      onChange={() => setEnhancementPattern('soft')}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">✈️ Soft News Only</div>
                      <div className="text-sm text-gray-600 mt-1">
                        Literary travel feature - storytelling style
                      </div>
                    </div>
                  </label>

                  <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                    style={{
                      borderColor: enhancementPattern === 'both' ? '#3b82f6' : '#e5e7eb',
                      backgroundColor: enhancementPattern === 'both' ? '#eff6ff' : 'white'
                    }}
                  >
                    <input
                      type="radio"
                      name="pattern"
                      value="both"
                      checked={enhancementPattern === 'both'}
                      onChange={() => setEnhancementPattern('both')}
                      className="mt-1 mr-3"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">📊 Both (Hard + Soft News)</div>
                      <div className="text-sm text-gray-600 mt-1">
                        Get both formats for different publishing needs
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                onClick={handleEnhance}
                isLoading={isEnhancing}
                disabled={isEnhancing}
                fullWidth
              >
                {isEnhancing ? 'Enhancing...' : 'Enhance Content'}
              </Button>
            </div>
          </Card>
        )}

        {/* Enhancement Results */}
        {enhancementResults && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Enhanced Results</h2>
              <Badge variant="success">
                {Object.keys(enhancementResults.formats).length} Format
                {Object.keys(enhancementResults.formats).length > 1 ? 's' : ''} • {enhancementResults.total_tokens_used} Tokens
              </Badge>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {Object.entries(enhancementResults.formats).map(([formatName, formatData]: [string, any]) => {
                const formatIcons: Record<string, string> = {
                  hard_news: '📰',
                  soft_news: '✈️',
                };
                const formatTitles: Record<string, string> = {
                  hard_news: 'Hard News - Professional Factual Reporting',
                  soft_news: 'Soft News - Literary Travel Feature',
                };

                return (
                  <Card
                    key={formatName}
                    className="bg-gradient-to-br from-purple-50 to-white border border-purple-200"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{formatIcons[formatName]}</span>
                        <h3 className="text-xl font-semibold text-gray-900">
                          {formatTitles[formatName]}
                        </h3>
                      </div>
                      <Badge variant="info" size="sm">
                        {formatData.tokens_used} tokens
                      </Badge>
                    </div>

                    <div className="prose prose-sm max-w-none mb-4">
                      <p className="text-gray-700 whitespace-pre-wrap">{formatData.content}</p>
                    </div>

                    <div className="flex gap-2 pt-4 border-t border-purple-200">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(formatData.content, formatTitles[formatName])}
                      >
                        Copy
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => downloadText(
                          formatData.content,
                          `${formatName}-${Date.now()}.txt`
                        )}
                      >
                        Download
                      </Button>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
