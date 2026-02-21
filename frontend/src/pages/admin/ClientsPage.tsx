/**
 * Admin Clients Page
 * Manage client configurations (multi-tenant settings)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { clientApi, formatApi, type ClientConfig, type ClientConfigCreate, type ClientConfigUpdate } from '../../api/admin';
import { AILoader } from '../../components/ui';
import {
  HiPlus,
  HiPencil,
  HiRefresh,
  HiX,
  HiCheck,
  HiUserGroup,
  HiOfficeBuilding,
  HiEyeOff,
  HiUserAdd,
  HiSwitchHorizontal,
} from 'react-icons/hi';

export const ClientsPage = () => {
  const queryClient = useQueryClient();
  const [showInactive, setShowInactive] = useState(false);
  const [editingClient, setEditingClient] = useState<ClientConfig | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [viewingUsers, setViewingUsers] = useState<ClientConfig | null>(null);
  const [formData, setFormData] = useState<Partial<ClientConfigCreate>>({});
  const [showAssignUser, setShowAssignUser] = useState(false);

  // Fetch clients
  const { data: clientsData, isLoading: clientsLoading, error: clientsError } = useQuery({
    queryKey: ['adminClients', showInactive],
    queryFn: () => clientApi.list(showInactive),
  });

  // Fetch formats for selection
  const { data: formatsData } = useQuery({
    queryKey: ['adminFormats', false],
    queryFn: () => formatApi.list(false),
  });

  // Fetch users for viewing
  const { data: clientUsers, isLoading: usersLoading } = useQuery({
    queryKey: ['clientUsers', viewingUsers?.id],
    queryFn: () => clientApi.listUsers(viewingUsers!.id),
    enabled: !!viewingUsers,
  });

  // Fetch all users for assignment
  const { data: allUsers, isLoading: allUsersLoading } = useQuery({
    queryKey: ['allUsersWithClients'],
    queryFn: () => clientApi.listAllUsers(),
    enabled: showAssignUser,
  });

  // Assign user mutation
  const assignUserMutation = useMutation({
    mutationFn: ({ userId, clientId }: { userId: number; clientId: number | null }) =>
      clientApi.assignUser(userId, clientId),
    onSuccess: () => {
      toast.success('User assigned successfully');
      queryClient.invalidateQueries({ queryKey: ['clientUsers'] });
      queryClient.invalidateQueries({ queryKey: ['allUsersWithClients'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to assign user');
    },
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: clientApi.create,
    onSuccess: () => {
      toast.success('Client created successfully');
      setIsCreating(false);
      setFormData({});
      queryClient.invalidateQueries({ queryKey: ['adminClients'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create client');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ClientConfigUpdate }) => clientApi.update(id, data),
    onSuccess: () => {
      toast.success('Client updated successfully');
      setEditingClient(null);
      setFormData({});
      queryClient.invalidateQueries({ queryKey: ['adminClients'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update client');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => clientApi.delete(id),
    onSuccess: () => {
      toast.success('Client deactivated');
      queryClient.invalidateQueries({ queryKey: ['adminClients'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete client');
    },
  });

  const handleStartCreate = () => {
    setIsCreating(true);
    setEditingClient(null);
    setFormData({
      name: '',
      slug: '',
      allowed_format_ids: [],
      default_format_id: undefined,
      ui_settings: {
        show_content_preview: true,
        workflow_type: 'full',
        show_format_selection: true,
        app_title: 'Swiftor',
      },
      display_overrides: {},
      is_active: true,
    });
  };

  const handleStartEdit = (client: ClientConfig) => {
    setEditingClient(client);
    setIsCreating(false);
    setFormData({
      name: client.name,
      slug: client.slug,
      allowed_format_ids: client.allowed_format_ids,
      default_format_id: client.default_format_id,
      ui_settings: client.ui_settings,
      display_overrides: client.display_overrides,
      is_active: client.is_active,
    });
  };

  const handleSave = () => {
    if (isCreating) {
      if (!formData.name || !formData.slug) {
        toast.error('Please fill in name and slug');
        return;
      }
      createMutation.mutate(formData as ClientConfigCreate);
    } else if (editingClient) {
      updateMutation.mutate({ id: editingClient.id, data: formData as ClientConfigUpdate });
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingClient(null);
    setFormData({});
  };

  const toggleFormatId = (formatId: number) => {
    const currentIds = formData.allowed_format_ids || [];
    const newIds = currentIds.includes(formatId)
      ? currentIds.filter(id => id !== formatId)
      : [...currentIds, formatId];
    setFormData({ ...formData, allowed_format_ids: newIds });
  };

  if (clientsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <AILoader text="Loading clients..." />
      </div>
    );
  }

  if (clientsError) {
    return (
      <div className="p-8 text-center text-red-500">
        Failed to load clients. Please try again.
      </div>
    );
  }

  const clients = clientsData?.clients || [];
  const formats = formatsData?.formats || [];

  return (
    <div className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Client Configurations</h1>
          <p className="text-gray-500 mt-1">Manage multi-tenant client settings and UI customizations</p>
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
            New Client
          </motion.button>
        </div>
      </div>

      {/* Clients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clients.map((client) => (
          <motion.div
            key={client.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-white rounded-2xl shadow-sm border border-gray-100 p-6 ${!client.is_active ? 'opacity-50' : ''}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
                  <HiOfficeBuilding className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{client.name}</h3>
                  <p className="text-sm text-gray-500 font-mono">{client.slug}</p>
                </div>
              </div>
              <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                client.is_active
                  ? 'bg-green-50 text-green-700'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {client.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Workflow</span>
                <span className="font-medium text-gray-900">{client.ui_settings?.workflow_type || 'full'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Formats</span>
                <span className="font-medium text-gray-900">{client.allowed_format_ids?.length || 0} allowed</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Content Preview</span>
                <span className={`font-medium ${client.ui_settings?.show_content_preview ? 'text-green-600' : 'text-gray-400'}`}>
                  {client.ui_settings?.show_content_preview ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-4 border-t border-gray-100">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setViewingUsers(client)}
                className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                title="View Users"
              >
                <HiUserGroup className="w-4 h-4" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => handleStartEdit(client)}
                className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                title="Edit"
              >
                <HiPencil className="w-4 h-4" />
              </motion.button>
              {client.is_active ? (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => deleteMutation.mutate(client.id)}
                  className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Deactivate"
                >
                  <HiEyeOff className="w-4 h-4" />
                </motion.button>
              ) : (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => updateMutation.mutate({ id: client.id, data: { is_active: true } })}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="Activate"
                >
                  <HiRefresh className="w-4 h-4" />
                </motion.button>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Edit/Create Modal */}
      <AnimatePresence>
        {(isCreating || editingClient) && (
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
              className="fixed inset-4 md:inset-10 lg:inset-20 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden flex flex-col"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">
                  {isCreating ? 'Create New Client' : `Edit ${editingClient?.name}`}
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
                  {/* Basic Info */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Basic Information</h3>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                      <input
                        type="text"
                        value={formData.name || ''}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="Banglar Columbus"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
                      <input
                        type="text"
                        value={formData.slug || ''}
                        onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                        placeholder="banglar_columbus"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
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

                    <h3 className="font-medium text-gray-900 pt-4">UI Settings</h3>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Workflow Type</label>
                      <select
                        value={formData.ui_settings?.workflow_type || 'full'}
                        onChange={(e) => setFormData({
                          ...formData,
                          ui_settings: {
                            ...formData.ui_settings,
                            workflow_type: e.target.value as 'full' | 'simple'
                          }
                        })}
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="full">Full (Content preview, format selection)</option>
                        <option value="simple">Simple (Direct processing)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">App Title</label>
                      <input
                        type="text"
                        value={formData.ui_settings?.app_title || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          ui_settings: { ...formData.ui_settings, app_title: e.target.value }
                        })}
                        placeholder="Swiftor"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={formData.ui_settings?.show_content_preview ?? true}
                          onChange={(e) => setFormData({
                            ...formData,
                            ui_settings: { ...formData.ui_settings, show_content_preview: e.target.checked }
                          })}
                          className="rounded border-gray-300"
                        />
                        Show content preview
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={formData.ui_settings?.show_format_selection ?? true}
                          onChange={(e) => setFormData({
                            ...formData,
                            ui_settings: { ...formData.ui_settings, show_format_selection: e.target.checked }
                          })}
                          className="rounded border-gray-300"
                        />
                        Show format selection
                      </label>
                    </div>

                    <h3 className="font-medium text-gray-900 pt-4">Export & Display Settings</h3>

                    <div className="space-y-2">
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={formData.ui_settings?.hide_format_labels ?? false}
                          onChange={(e) => setFormData({
                            ...formData,
                            ui_settings: { ...formData.ui_settings, hide_format_labels: e.target.checked }
                          })}
                          className="rounded border-gray-300"
                        />
                        Hide format type labels (হার্ড নিউজ/সফট নিউজ)
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={formData.ui_settings?.hide_main_content_export ?? false}
                          onChange={(e) => setFormData({
                            ...formData,
                            ui_settings: { ...formData.ui_settings, hide_main_content_export: e.target.checked }
                          })}
                          className="rounded border-gray-300"
                        />
                        Hide main content in Word exports
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Download Filename Prefix</label>
                      <input
                        type="text"
                        value={formData.ui_settings?.download_prefix || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          ui_settings: { ...formData.ui_settings, download_prefix: e.target.value }
                        })}
                        placeholder="Leave empty to use client name"
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                      <p className="text-xs text-gray-500 mt-1">Used as prefix in Word download filenames</p>
                    </div>
                  </div>

                  {/* Format Selection */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Allowed Formats</h3>

                    <div className="space-y-2">
                      {formats.map((format) => (
                        <label
                          key={format.id}
                          className={`flex items-center gap-3 p-3 border rounded-xl cursor-pointer transition-colors ${
                            formData.allowed_format_ids?.includes(format.id)
                              ? 'border-indigo-500 bg-indigo-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={formData.allowed_format_ids?.includes(format.id) || false}
                            onChange={() => toggleFormatId(format.id)}
                            className="rounded border-gray-300"
                          />
                          <div>
                            <div className="font-medium text-gray-900">{format.display_name}</div>
                            <div className="text-sm text-gray-500">{format.slug}</div>
                          </div>
                        </label>
                      ))}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Default Format</label>
                      <select
                        value={formData.default_format_id || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          default_format_id: e.target.value ? parseInt(e.target.value) : undefined
                        })}
                        className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        <option value="">Select default format</option>
                        {formats
                          .filter((f) => formData.allowed_format_ids?.includes(f.id))
                          .map((format) => (
                            <option key={format.id} value={format.id}>
                              {format.display_name}
                            </option>
                          ))}
                      </select>
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

      {/* Users Modal */}
      <AnimatePresence>
        {viewingUsers && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setViewingUsers(null)}
              className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 md:inset-20 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden flex flex-col max-w-2xl mx-auto"
            >
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Users - {viewingUsers.name}</h2>
                  <p className="text-sm text-gray-500">Users assigned to this client configuration</p>
                </div>
                <div className="flex items-center gap-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setShowAssignUser(true)}
                    className="flex items-center gap-2 px-3 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                  >
                    <HiUserAdd className="w-4 h-4" />
                    Assign User
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setViewingUsers(null)}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    <HiX className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                {usersLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <AILoader text="Loading users..." />
                  </div>
                ) : clientUsers && clientUsers.length > 0 ? (
                  <div className="space-y-3">
                    {clientUsers.map((user) => (
                      <div
                        key={user.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-xl"
                      >
                        <div>
                          <div className="font-medium text-gray-900">{user.full_name || user.email}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                        <div className="flex items-center gap-2">
                          {user.is_admin && (
                            <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                              Admin
                            </span>
                          )}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            user.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No users assigned to this client
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Assign User Modal */}
      <AnimatePresence>
        {showAssignUser && viewingUsers && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAssignUser(false)}
              className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[60]"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-4 md:inset-20 bg-white rounded-2xl shadow-2xl z-[60] overflow-hidden flex flex-col max-w-2xl mx-auto"
            >
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Assign User to {viewingUsers.name}</h2>
                  <p className="text-sm text-gray-500">Select a user to assign to this client</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setShowAssignUser(false)}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  <HiX className="w-5 h-5" />
                </motion.button>
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                {allUsersLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <AILoader text="Loading all users..." />
                  </div>
                ) : allUsers && allUsers.length > 0 ? (
                  <div className="space-y-3">
                    {allUsers.map((user) => {
                      const isAssignedHere = user.client_config_id === viewingUsers.id;
                      const isAssignedElsewhere = user.client_config_id && user.client_config_id !== viewingUsers.id;

                      return (
                        <div
                          key={user.id}
                          className={`flex items-center justify-between p-4 rounded-xl border transition-colors ${
                            isAssignedHere
                              ? 'bg-indigo-50 border-indigo-200'
                              : 'bg-gray-50 border-gray-100 hover:border-gray-200'
                          }`}
                        >
                          <div>
                            <div className="font-medium text-gray-900">{user.full_name || user.email}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                            {user.client && (
                              <div className="text-xs text-gray-400 mt-1">
                                Currently: {user.client.name}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            {user.is_admin && (
                              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                                Admin
                              </span>
                            )}
                            {isAssignedHere ? (
                              <span className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-medium">
                                Assigned Here
                              </span>
                            ) : (
                              <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => assignUserMutation.mutate({
                                  userId: user.id,
                                  clientId: viewingUsers.id
                                })}
                                disabled={assignUserMutation.isPending}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 ${
                                  isAssignedElsewhere
                                    ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                                }`}
                              >
                                {isAssignedElsewhere ? (
                                  <>
                                    <HiSwitchHorizontal className="w-3.5 h-3.5" />
                                    Reassign
                                  </>
                                ) : (
                                  <>
                                    <HiUserAdd className="w-3.5 h-3.5" />
                                    Assign
                                  </>
                                )}
                              </motion.button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No users found in the system
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end px-6 py-4 border-t border-gray-100">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowAssignUser(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-xl font-medium hover:bg-gray-200 transition-colors"
                >
                  Close
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
