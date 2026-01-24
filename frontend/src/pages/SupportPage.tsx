/**
 * Support Page - Contact form and ticket history
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { supportApi } from '../api/support';
import { useAuth } from '../contexts/AuthContext';
import { AILoader } from '../components/ui';
import type { SupportTicket, TicketStatus, TicketPriority, CreateTicketRequest, TicketWithUser } from '../types/support';
import {
  HiQuestionMarkCircle,
  HiPaperAirplane,
  HiClock,
  HiCheckCircle,
  HiExclamation,
  HiX,
  HiChat,
  HiChevronDown,
  HiRefresh,
  HiFilter,
  HiReply,
  HiShieldCheck,
} from 'react-icons/hi';

export const SupportPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'create' | 'history' | 'admin'>('create');
  const [expandedTicket, setExpandedTicket] = useState<number | null>(null);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [statusFilter, setStatusFilter] = useState<TicketStatus | ''>('');
  const [priorityFilter, setPriorityFilter] = useState<TicketPriority | ''>('');

  // Form state
  const [formData, setFormData] = useState<CreateTicketRequest>({
    subject: '',
    message: '',
    priority: 'medium',
  });

  // Fetch user's tickets
  const { data: myTickets, isLoading: ticketsLoading, refetch: refetchTickets } = useQuery({
    queryKey: ['myTickets'],
    queryFn: () => supportApi.getMyTickets(),
  });

  // Fetch admin tickets (only for admins)
  const { data: adminTickets, isLoading: adminTicketsLoading, refetch: refetchAdminTickets } = useQuery({
    queryKey: ['adminTickets', statusFilter, priorityFilter],
    queryFn: () => supportApi.adminGetAllTickets(
      statusFilter || undefined,
      priorityFilter || undefined
    ),
    enabled: user?.is_admin && activeTab === 'admin',
  });

  // Fetch admin stats
  const { data: adminStats } = useQuery({
    queryKey: ['adminSupportStats'],
    queryFn: supportApi.adminGetStats,
    enabled: user?.is_admin,
  });

  // Create ticket mutation
  const createTicketMutation = useMutation({
    mutationFn: supportApi.createTicket,
    onSuccess: () => {
      toast.success('Support ticket created successfully');
      setFormData({ subject: '', message: '', priority: 'medium' });
      setActiveTab('history');
      queryClient.invalidateQueries({ queryKey: ['myTickets'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create ticket');
    },
  });

  // User reply mutation
  const replyMutation = useMutation({
    mutationFn: ({ ticketId, message }: { ticketId: number; message: string }) =>
      supportApi.replyToTicket(ticketId, { message }),
    onSuccess: () => {
      toast.success('Reply sent');
      setReplyingTo(null);
      setReplyMessage('');
      queryClient.invalidateQueries({ queryKey: ['myTickets'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send reply');
    },
  });

  // Admin respond mutation
  const adminRespondMutation = useMutation({
    mutationFn: ({ ticketId, message }: { ticketId: number; message: string }) =>
      supportApi.adminRespond(ticketId, { message }),
    onSuccess: () => {
      toast.success('Response sent');
      setReplyingTo(null);
      setReplyMessage('');
      queryClient.invalidateQueries({ queryKey: ['adminTickets'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to send response');
    },
  });

  // Admin status update mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ ticketId, status }: { ticketId: number; status: TicketStatus }) =>
      supportApi.adminUpdateStatus(ticketId, { status }),
    onSuccess: (data) => {
      toast.success(data.message);
      queryClient.invalidateQueries({ queryKey: ['adminTickets'] });
      queryClient.invalidateQueries({ queryKey: ['adminSupportStats'] });
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update status');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.subject.length < 5) {
      toast.error('Subject must be at least 5 characters');
      return;
    }
    if (formData.message.length < 20) {
      toast.error('Message must be at least 20 characters');
      return;
    }
    createTicketMutation.mutate(formData);
  };

  const getStatusIcon = (status: TicketStatus) => {
    switch (status) {
      case 'open':
        return <HiExclamation className="w-4 h-4" />;
      case 'in_progress':
        return <HiClock className="w-4 h-4" />;
      case 'resolved':
        return <HiCheckCircle className="w-4 h-4" />;
      case 'closed':
        return <HiX className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: TicketStatus) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'in_progress':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'resolved':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'closed':
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getPriorityColor = (priority: TicketPriority) => {
    switch (priority) {
      case 'low':
        return 'bg-gray-100 text-gray-600';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'high':
        return 'bg-red-100 text-red-700';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Render ticket card
  const renderTicketCard = (ticket: SupportTicket | TicketWithUser, isAdmin: boolean = false) => {
    const isExpanded = expandedTicket === ticket.id;
    const ticketWithUser = ticket as TicketWithUser;

    return (
      <motion.div
        key={ticket.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
      >
        {/* Header */}
        <div
          className="p-4 cursor-pointer"
          onClick={() => setExpandedTicket(isExpanded ? null : ticket.id)}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(ticket.status)}`}>
                  {getStatusIcon(ticket.status)}
                  <span className="ml-1 capitalize">{ticket.status.replace('_', ' ')}</span>
                </span>
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getPriorityColor(ticket.priority)}`}>
                  {ticket.priority}
                </span>
                {ticket.replies.length > 0 && (
                  <span className="flex items-center gap-1 text-xs text-gray-500">
                    <HiChat className="w-3 h-3" />
                    {ticket.replies.length}
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-gray-900 truncate">{ticket.subject}</h3>
              {isAdmin && (
                <p className="text-sm text-gray-500 mt-1">
                  From: {ticketWithUser.user_email}
                </p>
              )}
              <p className="text-sm text-gray-500">{formatDate(ticket.created_at)}</p>
            </div>
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              className="text-gray-400"
            >
              <HiChevronDown className="w-5 h-5" />
            </motion.div>
          </div>
        </div>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-gray-200"
            >
              {/* Original Message */}
              <div className="p-4 bg-gray-50">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{ticket.message}</p>
              </div>

              {/* Replies */}
              {ticket.replies.length > 0 && (
                <div className="border-t border-gray-200">
                  {ticket.replies.map((reply) => (
                    <div
                      key={reply.id}
                      className={`p-4 border-b border-gray-100 last:border-b-0 ${
                        reply.is_admin_reply ? 'bg-indigo-50' : 'bg-white'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {reply.is_admin_reply && (
                          <HiShieldCheck className="w-4 h-4 text-indigo-600" />
                        )}
                        <span className="text-sm font-medium text-gray-900">
                          {reply.is_admin_reply ? 'Support Team' : reply.user_name || reply.user_email}
                        </span>
                        <span className="text-xs text-gray-500">{formatDate(reply.created_at)}</span>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{reply.message}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Reply Form */}
              {ticket.status !== 'closed' && (
                <div className="p-4 bg-gray-50 border-t border-gray-200">
                  {replyingTo === ticket.id ? (
                    <div className="space-y-3">
                      <textarea
                        value={replyMessage}
                        onChange={(e) => setReplyMessage(e.target.value)}
                        placeholder={isAdmin ? "Write your response..." : "Add more information..."}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            if (replyMessage.length < 10) {
                              toast.error('Reply must be at least 10 characters');
                              return;
                            }
                            if (isAdmin) {
                              adminRespondMutation.mutate({ ticketId: ticket.id, message: replyMessage });
                            } else {
                              replyMutation.mutate({ ticketId: ticket.id, message: replyMessage });
                            }
                          }}
                          disabled={replyMutation.isPending || adminRespondMutation.isPending}
                          className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
                        >
                          <HiPaperAirplane className="w-4 h-4 inline mr-1" />
                          Send
                        </motion.button>
                        <button
                          onClick={() => {
                            setReplyingTo(null);
                            setReplyMessage('');
                          }}
                          className="px-4 py-2 text-gray-600 hover:bg-gray-200 rounded-lg"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setReplyingTo(ticket.id)}
                      className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      <HiReply className="w-4 h-4" />
                      {isAdmin ? 'Respond' : 'Add Reply'}
                    </button>
                  )}
                </div>
              )}

              {/* Admin Status Update */}
              {isAdmin && ticket.status !== 'closed' && (
                <div className="p-4 bg-amber-50 border-t border-amber-200">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-amber-800">Update Status:</span>
                    {(['open', 'in_progress', 'resolved', 'closed'] as TicketStatus[]).map((status) => (
                      <button
                        key={status}
                        onClick={() => updateStatusMutation.mutate({ ticketId: ticket.id, status })}
                        disabled={ticket.status === status || updateStatusMutation.isPending}
                        className={`px-3 py-1 text-xs font-medium rounded-full border transition-colors ${
                          ticket.status === status
                            ? 'opacity-50 cursor-not-allowed ' + getStatusColor(status)
                            : 'bg-white border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        {status.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-indigo-50/30 to-purple-50/40" />
      </div>

      <motion.div
        className="w-full max-w-[95vw] lg:max-w-[90vw] 2xl:max-w-[85vw] mx-auto px-4 sm:px-6 lg:px-8 py-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="mb-8"
        >
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-xl">
              <HiQuestionMarkCircle className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-indigo-800 to-purple-800 bg-clip-text text-transparent">
                Support Center
              </h1>
              <p className="text-gray-500 mt-1">Get help with Swiftor</p>
            </div>
          </div>
        </motion.div>

        {/* Admin Stats */}
        {user?.is_admin && adminStats && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8"
          >
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <p className="text-2xl font-bold text-gray-900">{adminStats.total_tickets}</p>
              <p className="text-sm text-gray-500">Total Tickets</p>
            </div>
            <div className="bg-blue-50 p-4 rounded-xl border border-blue-200">
              <p className="text-2xl font-bold text-blue-600">{adminStats.open}</p>
              <p className="text-sm text-blue-600">Open</p>
            </div>
            <div className="bg-amber-50 p-4 rounded-xl border border-amber-200">
              <p className="text-2xl font-bold text-amber-600">{adminStats.in_progress}</p>
              <p className="text-sm text-amber-600">In Progress</p>
            </div>
            <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-200">
              <p className="text-2xl font-bold text-emerald-600">{adminStats.resolved}</p>
              <p className="text-sm text-emerald-600">Resolved</p>
            </div>
            <div className="bg-gray-100 p-4 rounded-xl border border-gray-200">
              <p className="text-2xl font-bold text-gray-600">{adminStats.closed}</p>
              <p className="text-sm text-gray-500">Closed</p>
            </div>
            <div className="bg-red-50 p-4 rounded-xl border border-red-200">
              <p className="text-2xl font-bold text-red-600">{adminStats.high_priority_pending}</p>
              <p className="text-sm text-red-600">High Priority</p>
            </div>
          </motion.div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('create')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'create'
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            <HiPaperAirplane className="w-4 h-4 inline mr-2" />
            New Ticket
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            <HiClock className="w-4 h-4 inline mr-2" />
            My Tickets
            {myTickets && myTickets.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-xs">
                {myTickets.length}
              </span>
            )}
          </button>
          {user?.is_admin && (
            <button
              onClick={() => setActiveTab('admin')}
              className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                activeTab === 'admin'
                  ? 'bg-amber-500 text-white shadow-lg'
                  : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200'
              }`}
            >
              <HiShieldCheck className="w-4 h-4 inline mr-2" />
              Admin View
            </button>
          )}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'create' && (
            <motion.div
              key="create"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6 max-w-2xl"
            >
              <h2 className="text-xl font-bold text-gray-900 mb-6">Create Support Ticket</h2>
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    placeholder="Brief description of your issue"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    maxLength={200}
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">{formData.subject.length}/200 characters</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority
                  </label>
                  <div className="flex gap-3">
                    {(['low', 'medium', 'high'] as TicketPriority[]).map((priority) => (
                      <button
                        key={priority}
                        type="button"
                        onClick={() => setFormData({ ...formData, priority })}
                        className={`flex-1 py-2 px-4 rounded-xl font-medium border-2 transition-all ${
                          formData.priority === priority
                            ? priority === 'high'
                              ? 'border-red-500 bg-red-50 text-red-700'
                              : priority === 'medium'
                              ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                              : 'border-gray-400 bg-gray-50 text-gray-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {priority.charAt(0).toUpperCase() + priority.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    placeholder="Please describe your issue in detail..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                    rows={6}
                    maxLength={5000}
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">{formData.message.length}/5000 characters</p>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  disabled={createTicketMutation.isPending}
                  className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl disabled:opacity-50 transition-all"
                >
                  {createTicketMutation.isPending ? (
                    <span className="flex items-center justify-center gap-2">
                      <AILoader variant="dots" size="sm" />
                      Submitting...
                    </span>
                  ) : (
                    <>
                      <HiPaperAirplane className="w-5 h-5 inline mr-2" />
                      Submit Ticket
                    </>
                  )}
                </motion.button>
              </form>
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">My Tickets</h2>
                <button
                  onClick={() => refetchTickets()}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <HiRefresh className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {ticketsLoading ? (
                <div className="flex justify-center py-12">
                  <AILoader variant="neural" size="lg" text="Loading tickets..." />
                </div>
              ) : myTickets && myTickets.length > 0 ? (
                <div className="space-y-4">
                  {myTickets.map((ticket) => renderTicketCard(ticket, false))}
                </div>
              ) : (
                <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
                  <HiQuestionMarkCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 font-medium">No tickets yet</p>
                  <button
                    onClick={() => setActiveTab('create')}
                    className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700"
                  >
                    Create Your First Ticket
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'admin' && user?.is_admin && (
            <motion.div
              key="admin"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between flex-wrap gap-4 mb-4">
                <h2 className="text-xl font-bold text-gray-900">All Support Tickets</h2>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <HiFilter className="w-4 h-4 text-gray-500" />
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value as TicketStatus | '')}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="">All Status</option>
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                    <select
                      value={priorityFilter}
                      onChange={(e) => setPriorityFilter(e.target.value as TicketPriority | '')}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    >
                      <option value="">All Priority</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  <button
                    onClick={() => refetchAdminTickets()}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <HiRefresh className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>

              {adminTicketsLoading ? (
                <div className="flex justify-center py-12">
                  <AILoader variant="neural" size="lg" text="Loading tickets..." />
                </div>
              ) : adminTickets && adminTickets.length > 0 ? (
                <div className="space-y-4">
                  {adminTickets.map((ticket) => renderTicketCard(ticket, true))}
                </div>
              ) : (
                <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
                  <HiCheckCircle className="w-16 h-16 mx-auto text-emerald-300 mb-4" />
                  <p className="text-gray-500 font-medium">No tickets match your filters</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};
