/**
 * Admin: Sources Management Page
 * Enable/disable news sources in sites_config.json
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosInstance from '../../services/axios';
import toast from 'react-hot-toast';
import { HiGlobe, HiTrash, HiCheck, HiBan } from 'react-icons/hi';

interface Source {
  name: string;
  description: string;
  url: string;
  language: string;
  disabled: boolean;
  article_count: number;
}

const fetchSources = async (): Promise<{ sources: Source[]; total: number }> => {
  const res = await axiosInstance.get('/admin/sources');
  return res.data;
};

export const SourcesPage = () => {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ['adminSources'], queryFn: fetchSources });
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const toggleMutation = useMutation({
    mutationFn: ({ name, disable }: { name: string; disable: boolean }) =>
      axiosInstance.patch(`/admin/sources/${name}/${disable ? 'disable' : 'enable'}`),
    onSuccess: (_, { name, disable }) => {
      toast.success(`${name} ${disable ? 'disabled' : 'enabled'}`);
      queryClient.invalidateQueries({ queryKey: ['adminSources'] });
    },
    onError: () => toast.error('Failed to update source'),
  });

  const deleteMutation = useMutation({
    mutationFn: (name: string) => axiosInstance.delete(`/admin/sources/${name}`),
    onSuccess: (_, name) => {
      toast.success(`${name} removed`);
      setConfirmDelete(null);
      queryClient.invalidateQueries({ queryKey: ['adminSources'] });
    },
    onError: () => toast.error('Failed to delete source'),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const sources = data?.sources || [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FAF8F5] to-[#F5F3F0]">
      <div className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Sources Management</h1>
          <p className="text-gray-500 mt-1">
            {sources.length} sources configured. Disabled sources are excluded from scraping and filters.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-100 bg-gray-50">
                <th className="px-6 py-3 font-medium">Source</th>
                <th className="px-6 py-3 font-medium">Description</th>
                <th className="px-6 py-3 font-medium">Lang</th>
                <th className="px-6 py-3 font-medium text-right">Articles</th>
                <th className="px-6 py-3 font-medium text-center">Status</th>
                <th className="px-6 py-3 w-28"></th>
              </tr>
            </thead>
            <tbody>
              {sources.map((source) => (
                <tr key={source.name} className={`border-b border-gray-50 hover:bg-gray-50 ${source.disabled ? 'opacity-60' : ''}`}>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <HiGlobe className="w-4 h-4 text-gray-400 shrink-0" />
                      <span className="font-mono font-medium text-gray-800">{source.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-600 max-w-xs truncate">{source.description}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-mono">{source.language}</span>
                  </td>
                  <td className="px-6 py-4 text-right text-gray-600">{source.article_count.toLocaleString()}</td>
                  <td className="px-6 py-4 text-center">
                    {source.disabled ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                        <HiBan className="w-3 h-3" /> Disabled
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        <HiCheck className="w-3 h-3" /> Active
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 justify-end">
                      <button
                        onClick={() => toggleMutation.mutate({ name: source.name, disable: !source.disabled })}
                        disabled={toggleMutation.isPending}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          source.disabled
                            ? 'bg-green-100 text-green-700 hover:bg-green-200'
                            : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                        }`}
                      >
                        {source.disabled ? 'Enable' : 'Disable'}
                      </button>
                      {confirmDelete === source.name ? (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => deleteMutation.mutate(source.name)}
                            disabled={deleteMutation.isPending}
                            className="px-2 py-1.5 bg-red-600 text-white rounded-lg text-xs font-medium hover:bg-red-700"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmDelete(null)}
                            className="px-2 py-1.5 bg-gray-100 text-gray-600 rounded-lg text-xs font-medium hover:bg-gray-200"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDelete(source.name)}
                          className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <HiTrash className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-gray-400">
          Note: To edit scraper selectors or URLs, modify <code>config/sites_config.json</code> directly.
        </p>
      </div>
    </div>
  );
};
