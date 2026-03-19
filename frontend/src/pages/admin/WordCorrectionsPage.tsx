/**
 * Admin: Word Corrections Page
 * Manage English→Bengali replacements and Bengali spelling corrections
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '../../services/axios';
import toast from 'react-hot-toast';
import { HiPlus, HiTrash, HiSave, HiCheck, HiX } from 'react-icons/hi';
import { wordCorrectionsApi } from '../../services/api';

interface BengaliCorrection {
  pattern: string;
  replacement: string;
}

interface WordCorrectionsData {
  english_to_bengali: Record<string, string>;
  bengali_corrections: BengaliCorrection[];
}

interface WordSuggestion {
  id: string;
  english: string;
  bengali: string;
  suggested_by: string;
  suggested_at: string;
}

const fetchCorrections = async (): Promise<WordCorrectionsData> => {
  const res = await axiosInstance.get('/api/admin/word-corrections');
  return res.data;
};

const saveCorrections = async (data: WordCorrectionsData): Promise<WordCorrectionsData> => {
  const res = await axiosInstance.post('/api/admin/word-corrections', data);
  return res.data;
};

export const WordCorrectionsPage = () => {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['wordCorrections'], queryFn: fetchCorrections });

  const [e2bEntries, setE2bEntries] = useState<[string, string][]>([]);
  const [bnCorrections, setBnCorrections] = useState<BengaliCorrection[]>([]);

  const [newEnglish, setNewEnglish] = useState('');
  const [newBengali, setNewBengali] = useState('');
  const [newBnPattern, setNewBnPattern] = useState('');
  const [newBnReplacement, setNewBnReplacement] = useState('');

  // Populate local state when data arrives
  useEffect(() => {
    if (data) {
      setE2bEntries(Object.entries(data.english_to_bengali));
      setBnCorrections(data.bengali_corrections);
    }
  }, [data]);

  const { data: suggestions = [] } = useQuery<WordSuggestion[]>({
    queryKey: ['wordSuggestions'],
    queryFn: wordCorrectionsApi.getSuggestions,
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => wordCorrectionsApi.approveSuggestion(id),
    onSuccess: () => {
      toast.success('Added to corrections');
      queryClient.invalidateQueries({ queryKey: ['wordSuggestions'] });
      queryClient.invalidateQueries({ queryKey: ['wordCorrections'] });
    },
    onError: () => toast.error('Failed to approve'),
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => wordCorrectionsApi.rejectSuggestion(id),
    onSuccess: () => {
      toast.success('Suggestion rejected');
      queryClient.invalidateQueries({ queryKey: ['wordSuggestions'] });
    },
    onError: () => toast.error('Failed to reject'),
  });

  const saveMutation = useMutation({
    mutationFn: saveCorrections,
    onSuccess: () => {
      toast.success('Saved. Changes apply on next server restart.');
      queryClient.invalidateQueries({ queryKey: ['wordCorrections'] });
    },
    onError: () => toast.error('Failed to save'),
  });

  const handleSave = () => {
    const english_to_bengali = Object.fromEntries(e2bEntries);
    saveMutation.mutate({ english_to_bengali, bengali_corrections: bnCorrections });
  };

  const addE2B = () => {
    const key = newEnglish.trim();
    const val = newBengali.trim();
    if (!key || !val) return;
    if (e2bEntries.some(([k]) => k === key)) {
      toast.error(`"${key}" already exists`);
      return;
    }
    setE2bEntries([...e2bEntries, [key, val]]);
    setNewEnglish('');
    setNewBengali('');
  };

  const removeE2B = (index: number) => {
    setE2bEntries(e2bEntries.filter((_, i) => i !== index));
  };

  const addBnCorrection = () => {
    const pattern = newBnPattern.trim();
    const replacement = newBnReplacement.trim();
    if (!pattern) return;
    setBnCorrections([...bnCorrections, { pattern, replacement }]);
    setNewBnPattern('');
    setNewBnReplacement('');
  };

  const removeBnCorrection = (index: number) => {
    setBnCorrections(bnCorrections.filter((_, i) => i !== index));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FAF8F5] to-[#F5F3F0]">
      <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Word Corrections</h1>
            <p className="text-gray-500 mt-1">Applied after AI generation. Changes take effect on next server restart.</p>
          </div>
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-sm"
          >
            <HiSave className="w-5 h-5" />
            {saveMutation.isPending ? 'Saving...' : 'Save All'}
          </button>
        </div>

        {/* English → Bengali */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm mb-6 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">English → Bengali Replacements</h2>
            <p className="text-sm text-gray-500">English words replaced with Bengali equivalents in generated text</p>
          </div>

          {/* Add row */}
          <div className="px-6 py-4 border-b border-gray-100 flex gap-3">
            <input
              type="text"
              value={newEnglish}
              onChange={e => setNewEnglish(e.target.value)}
              placeholder="English word"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              onKeyDown={e => e.key === 'Enter' && addE2B()}
            />
            <input
              type="text"
              value={newBengali}
              onChange={e => setNewBengali(e.target.value)}
              placeholder="Bengali replacement"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              onKeyDown={e => e.key === 'Enter' && addE2B()}
            />
            <button
              onClick={addE2B}
              className="inline-flex items-center gap-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              <HiPlus className="w-4 h-4" /> Add
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            {e2bEntries.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-400">
                No user-defined entries. Add one above.
                <p className="text-xs mt-1 text-gray-300">Hardcoded defaults (graceful, elegant, etc.) are always applied.</p>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="px-6 py-3 font-medium">English</th>
                    <th className="px-6 py-3 font-medium">Bengali</th>
                    <th className="px-6 py-3 w-16"></th>
                  </tr>
                </thead>
                <tbody>
                  {e2bEntries.map(([eng, bn], i) => (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="px-6 py-3 font-mono text-gray-700">{eng}</td>
                      <td className="px-6 py-3 text-gray-700">{bn}</td>
                      <td className="px-6 py-3">
                        <button
                          onClick={() => removeE2B(i)}
                          className="text-red-400 hover:text-red-600 transition-colors"
                        >
                          <HiTrash className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Pending Suggestions */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm mb-6 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-amber-50 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                Pending User Suggestions
                {suggestions.length > 0 && (
                  <span className="inline-flex items-center justify-center w-6 h-6 bg-amber-500 text-white text-xs font-bold rounded-full">
                    {suggestions.length}
                  </span>
                )}
              </h2>
              <p className="text-sm text-gray-500">Review and approve English→Bengali word suggestions from users</p>
            </div>
          </div>
          {suggestions.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-400">No pending suggestions.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="px-6 py-3 font-medium">English</th>
                  <th className="px-6 py-3 font-medium">Bengali</th>
                  <th className="px-6 py-3 font-medium">Suggested by</th>
                  <th className="px-6 py-3 w-24"></th>
                </tr>
              </thead>
              <tbody>
                {suggestions.map((s) => (
                  <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="px-6 py-3 font-mono text-gray-700">{s.english}</td>
                    <td className="px-6 py-3 text-gray-700">{s.bengali}</td>
                    <td className="px-6 py-3 text-gray-500 text-xs">{s.suggested_by}</td>
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => approveMutation.mutate(s.id)}
                          disabled={approveMutation.isPending}
                          title="Approve"
                          className="text-emerald-500 hover:text-emerald-700 transition-colors disabled:opacity-50"
                        >
                          <HiCheck className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => rejectMutation.mutate(s.id)}
                          disabled={rejectMutation.isPending}
                          title="Reject"
                          className="text-red-400 hover:text-red-600 transition-colors disabled:opacity-50"
                        >
                          <HiX className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Bengali Corrections */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Bengali Spelling Corrections</h2>
            <p className="text-sm text-gray-500">Regex pattern → replacement (e.g. শীঘ্রই → শিগগিরই)</p>
          </div>

          {/* Add row */}
          <div className="px-6 py-4 border-b border-gray-100 flex gap-3">
            <input
              type="text"
              value={newBnPattern}
              onChange={e => setNewBnPattern(e.target.value)}
              placeholder="Pattern (regex or plain text)"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              onKeyDown={e => e.key === 'Enter' && addBnCorrection()}
            />
            <input
              type="text"
              value={newBnReplacement}
              onChange={e => setNewBnReplacement(e.target.value)}
              placeholder="Replacement"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              onKeyDown={e => e.key === 'Enter' && addBnCorrection()}
            />
            <button
              onClick={addBnCorrection}
              className="inline-flex items-center gap-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              <HiPlus className="w-4 h-4" /> Add
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            {bnCorrections.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-400">
                No user-defined corrections. Add one above.
                <p className="text-xs mt-1 text-gray-300">Hardcoded defaults (শীঘ্রই→শিগগিরই, etc.) are always applied.</p>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="px-6 py-3 font-medium">Pattern</th>
                    <th className="px-6 py-3 font-medium">Replacement</th>
                    <th className="px-6 py-3 w-16"></th>
                  </tr>
                </thead>
                <tbody>
                  {bnCorrections.map((c, i) => (
                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="px-6 py-3 font-mono text-gray-700">{c.pattern}</td>
                      <td className="px-6 py-3 text-gray-700">{c.replacement}</td>
                      <td className="px-6 py-3">
                        <button
                          onClick={() => removeBnCorrection(i)}
                          className="text-red-400 hover:text-red-600 transition-colors"
                        >
                          <HiTrash className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
