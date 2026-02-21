/**
 * Admin Formats Page
 * Manage content format configurations (hard_news, soft_news, etc.)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { formatApi, type FormatConfig, type FormatConfigCreate, type FormatConfigUpdate } from '../../api/admin';
import { AILoader } from '../../components/ui';
import {
  HiPlus,
  HiPencil,
  HiRefresh,
  HiX,
  HiCheck,
  HiEyeOff,
  HiNewspaper,
  HiBookOpen,
  HiSparkles,
  HiDocumentText,
  HiOfficeBuilding,
  HiStar,
} from 'react-icons/hi';

// Icon mapping
const iconMap: Record<string, React.ReactNode> = {
  newspaper: <HiNewspaper className="w-5 h-5" />,
  book: <HiBookOpen className="w-5 h-5" />,
  sparkles: <HiSparkles className="w-5 h-5" />,
  document: <HiDocumentText className="w-5 h-5" />,
};

const iconOptions = ['newspaper', 'book', 'sparkles', 'document'];

export const FormatsPage = () => {
  const queryClient = useQueryClient();
  const [showInactive, setShowInactive] = useState(false);
  const [editingFormat, setEditingFormat] = useState<FormatConfig | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<Partial<FormatConfigCreate>>({});
  const [viewingClientsFormat, setViewingClientsFormat] = useState<FormatConfig | null>(null);

  // Fetch formats
  const { data, isLoading, error } = useQuery({
    queryKey: ['adminFormats', showInactive],
    queryFn: () => formatApi.list(showInactive),
  });

  // Fetch clients for a format
  const { data: formatClients, isLoading: clientsLoading } = useQuery({
    queryKey: ['formatClients', viewingClientsFormat?.id],
    queryFn: () => formatApi.getClients(viewingClientsFormat!.id),
    enabled: !!viewingClientsFormat,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: formatApi.create,
    onSuccess: () => {
      toast.success('Format created successfully');
      setIsCreating(false);
      setFormData({});
      queryClient.invalidateQueries({ queryKey: ['adminFormats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create format');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: FormatConfigUpdate }) => formatApi.update(id, data),
    onSuccess: () => {
      toast.success('Format updated successfully');
      setEditingFormat(null);
      setFormData({});
      queryClient.invalidateQueries({ queryKey: ['adminFormats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update format');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => formatApi.delete(id),
    onSuccess: () => {
      toast.success('Format deactivated');
      queryClient.invalidateQueries({ queryKey: ['adminFormats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete format');
    },
  });

  const restoreMutation = useMutation({
    mutationFn: formatApi.restore,
    onSuccess: () => {
      toast.success('Format restored');
      queryClient.invalidateQueries({ queryKey: ['adminFormats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to restore format');
    },
  });

  const updateRule = (key: string, value: unknown) => {
    const currentRules = formData.rules || {};
    if (value === null || value === undefined || value === '') {
      const { [key]: _, ...rest } = currentRules as Record<string, unknown>;
      setFormData({ ...formData, rules: rest });
    } else {
      setFormData({ ...formData, rules: { ...currentRules, [key]: value } });
    }
  };

  const handleStartCreate = () => {
    setIsCreating(true);
    setEditingFormat(null);
    setFormData({
      slug: '',
      display_name: '',
      description: '',
      icon: 'newspaper',
      system_prompt: '',
      temperature: 0.5,
      max_tokens: 4096,
      rules: {},
      is_active: true,
    });
  };

  const handleStartEdit = (format: FormatConfig) => {
    setEditingFormat(format);
    setIsCreating(false);
    setFormData({
      slug: format.slug,
      display_name: format.display_name,
      description: format.description || '',
      icon: format.icon,
      system_prompt: format.system_prompt,
      temperature: format.temperature,
      max_tokens: format.max_tokens,
      rules: format.rules,
      is_active: format.is_active,
    });
  };

  const handleSave = () => {
    if (isCreating) {
      if (!formData.slug || !formData.display_name || !formData.system_prompt) {
        toast.error('Please fill in all required fields');
        return;
      }
      createMutation.mutate(formData as FormatConfigCreate);
    } else if (editingFormat) {
      updateMutation.mutate({ id: editingFormat.id, data: formData as FormatConfigUpdate });
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingFormat(null);
    setFormData({});
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <AILoader text="Loading formats..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-500">
        Failed to load formats. Please try again.
      </div>
    );
  }

  const formats = data?.formats || [];

  return (
    <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Format Configurations</h1>
          <p className="text-gray-500 mt-1">Manage content generation formats and prompts</p>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
              className="rounded border-gray-300"
            />
            Show inactive
          </label>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleStartCreate}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
          >
            <HiPlus className="w-5 h-5" />
            New Format
          </motion.button>
        </div>
      </div>

      {/* Formats Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Format</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Slug</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Temperature</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Max Tokens</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Status</th>
              <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {formats.map((format) => (
              <tr key={format.id} className={`hover:bg-gray-50 ${!format.is_active ? 'opacity-50' : ''}`}>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                      {iconMap[format.icon] || <HiDocumentText className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{format.display_name}</div>
                      <div className="text-sm text-gray-500">{format.description}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">{format.slug}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{format.temperature}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{format.max_tokens}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                    format.is_active
                      ? 'bg-green-50 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {format.is_active ? <HiCheck className="w-3 h-3" /> : <HiX className="w-3 h-3" />}
                    {format.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end gap-2">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => setViewingClientsFormat(format)}
                      className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="View Clients"
                    >
                      <HiOfficeBuilding className="w-4 h-4" />
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => handleStartEdit(format)}
                      className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <HiPencil className="w-4 h-4" />
                    </motion.button>
                    {format.is_active ? (
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => deleteMutation.mutate(format.id)}
                        className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Deactivate"
                      >
                        <HiEyeOff className="w-4 h-4" />
                      </motion.button>
                    ) : (
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => restoreMutation.mutate(format.id)}
                        className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Restore"
                      >
                        <HiRefresh className="w-4 h-4" />
                      </motion.button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* View Clients Modal */}
      <AnimatePresence>
        {viewingClientsFormat && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setViewingClientsFormat(null)}
              className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 md:inset-20 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden flex flex-col max-w-2xl mx-auto"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Clients Using "{viewingClientsFormat.display_name}"
                  </h2>
                  <p className="text-sm text-gray-500">
                    {formatClients?.total || 0} client(s) have access to this format
                  </p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setViewingClientsFormat(null)}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  <HiX className="w-5 h-5" />
                </motion.button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {clientsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <AILoader text="Loading clients..." />
                  </div>
                ) : formatClients?.clients && formatClients.clients.length > 0 ? (
                  <div className="space-y-3">
                    {formatClients.clients.map((client) => (
                      <div
                        key={client.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                      >
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-purple-100 text-purple-600 rounded-lg">
                            <HiOfficeBuilding className="w-5 h-5" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{client.name}</div>
                            <div className="text-sm text-gray-500 font-mono">{client.slug}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {client.display_override && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                              Renamed: {client.display_override}
                            </span>
                          )}
                          {client.is_default && (
                            <span className="flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
                              <HiStar className="w-3 h-3" />
                              Default
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <HiOfficeBuilding className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>No clients are using this format</p>
                    <p className="text-sm mt-1">Go to Clients page to assign this format</p>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Edit/Create Modal */}
      <AnimatePresence>
        {(isCreating || editingFormat) && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={handleCancel}
              className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 md:inset-10 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden flex flex-col"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                  {isCreating ? 'Create New Format' : `Edit ${editingFormat?.display_name}`}
                </h2>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleCancel}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  <HiX className="w-5 h-5" />
                </motion.button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-y-auto p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
                      <input
                        type="text"
                        value={formData.slug || ''}
                        onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                        placeholder="hard_news"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Display Name *</label>
                      <input
                        type="text"
                        value={formData.display_name || ''}
                        onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                        placeholder="Hard News"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <input
                        type="text"
                        value={formData.description || ''}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="Professional factual news"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Icon</label>
                      <div className="flex gap-2">
                        {iconOptions.map((icon) => (
                          <button
                            key={icon}
                            onClick={() => setFormData({ ...formData, icon })}
                            className={`p-3 rounded-xl border-2 transition-colors ${
                              formData.icon === icon
                                ? 'border-indigo-500 bg-indigo-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            {iconMap[icon]}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="2"
                          value={formData.temperature ?? 0.5}
                          onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
                        <input
                          type="number"
                          min="100"
                          max="16000"
                          value={formData.max_tokens ?? 4096}
                          onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                        <input
                          type="checkbox"
                          checked={formData.is_active ?? true}
                          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                          className="rounded border-gray-300"
                        />
                        Active
                      </label>
                    </div>
                  </div>

                  {/* Right Column - System Prompt + Rules */}
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt *</label>
                      <textarea
                        value={formData.system_prompt || ''}
                        onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                        rows={14}
                        placeholder="Enter the AI system prompt..."
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm"
                      />
                    </div>

                    {/* Post-Processing Rules */}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 border-b border-gray-100 pb-2">Post-Processing Rules</h3>
                      <div className="space-y-3">
                        {/* Allow Subheads */}
                        <label className="flex items-center gap-2 text-sm text-gray-700">
                          <input
                            type="checkbox"
                            checked={formData.rules?.allow_subheads ?? true}
                            onChange={(e) => updateRule('allow_subheads', e.target.checked)}
                            className="rounded border-gray-300"
                          />
                          Allow Subheads
                        </label>

                        <div className="grid grid-cols-2 gap-3">
                          {/* Max Intro Sentences */}
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Max Intro Sentences</label>
                            <input
                              type="number"
                              min="1"
                              max="6"
                              value={formData.rules?.intro_max_sentences ?? ''}
                              onChange={(e) => updateRule('intro_max_sentences', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="e.g. 3"
                              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                          </div>

                          {/* Intro Paragraphs Before Subhead */}
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Intros Before Subhead</label>
                            <input
                              type="number"
                              min="0"
                              max="3"
                              value={formData.rules?.intro_paragraphs_before_subhead ?? ''}
                              onChange={(e) => updateRule('intro_paragraphs_before_subhead', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="e.g. 2"
                              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                          </div>

                          {/* Min Words */}
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Min Words</label>
                            <input
                              type="number"
                              min="0"
                              value={formData.rules?.min_words ?? ''}
                              onChange={(e) => updateRule('min_words', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="e.g. 220"
                              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                          </div>

                          {/* Max Words */}
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Max Words</label>
                            <input
                              type="number"
                              min="0"
                              value={formData.rules?.max_words ?? ''}
                              onChange={(e) => updateRule('max_words', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="e.g. 450"
                              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                          </div>

                          {/* Max Sentences Per Paragraph */}
                          <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Max Sentences/Para</label>
                            <input
                              type="number"
                              min="0"
                              max="5"
                              value={formData.rules?.max_sentences_per_paragraph ?? ''}
                              onChange={(e) => updateRule('max_sentences_per_paragraph', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="e.g. 2"
                              className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCancel}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-xl font-medium hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSave}
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  <HiCheck className="w-5 h-5" />
                  {isCreating ? 'Create' : 'Save Changes'}
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
