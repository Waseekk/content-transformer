import { useState } from 'react';
import { Button, Textarea, Card } from '../common';
import { extractAndTranslate, translateText } from '../../api/translation';
import toast from 'react-hot-toast';

interface TranslationFormProps {
  onTranslationComplete?: (translation: any) => void;
}

export function TranslationForm({ onTranslationComplete }: TranslationFormProps) {
  const [mode, setMode] = useState<'url' | 'text'>('url');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);

    try {
      let translation;
      if (mode === 'url') {
        if (!url.trim()) {
          toast.error('Please enter a URL');
          return;
        }
        translation = await extractAndTranslate(url);
        toast.success('Content extracted and translated successfully!');
      } else {
        if (!text.trim()) {
          toast.error('Please enter text to translate');
          return;
        }
        translation = await translateText(text);
        toast.success('Text translated successfully!');
      }

      // Map backend response to frontend format
      const mappedResult = {
        headline: translation.headline || 'Translation',
        content: translation.content,
        tokens_used: translation.tokens_used,
        id: translation.id,
      };

      setResult(mappedResult);
      if (onTranslationComplete) {
        onTranslationComplete(mappedResult);
      }

      // Clear form
      setUrl('');
      setText('');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Translation failed';
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setUrl('');
    setText('');
    setResult(null);
  };

  return (
    <div className="space-y-6">
      <Card title="Translate Content" subtitle="Extract and translate travel news to Bengali">
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

        <form onSubmit={handleSubmit} className="space-y-4">
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
                disabled={isLoading}
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
              rows={8}
              disabled={isLoading}
              helperText="Paste the article text you want to translate to Bengali"
            />
          )}

          <div className="flex gap-3">
            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {mode === 'url' ? 'Extract & Translate' : 'Translate'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={handleClear}
              disabled={isLoading}
            >
              Clear
            </Button>
          </div>
        </form>
      </Card>

      {result && (
        <Card title="Translation Result" className="bg-green-50 border border-green-200">
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {result.headline}
              </h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{result.content}</p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-green-300">
              <div className="text-sm text-gray-600">
                <span className="font-medium">Tokens used:</span> {result.tokens_used}
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(result.content);
                    toast.success('Translation copied to clipboard!');
                  }}
                >
                  Copy
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    const blob = new Blob([`${result.headline}\n\n${result.content}`], {
                      type: 'text/plain',
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `translation-${Date.now()}.txt`;
                    a.click();
                    URL.revokeObjectURL(url);
                    toast.success('Translation downloaded!');
                  }}
                >
                  Download
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
