import api from './axios';
import type {
  SupportTicket,
  TicketWithUser,
  TicketReply,
  TicketAttachment,
  CreateTicketRequest,
  TicketReplyRequest,
  UpdateTicketStatusRequest,
  SupportStats,
  TicketStatus,
  TicketPriority,
} from '../types/support';

export const supportApi = {
  // User: Create a new ticket (JSON, no files)
  createTicket: async (data: CreateTicketRequest): Promise<SupportTicket> => {
    const response = await api.post<SupportTicket>('/api/support/tickets', data);
    return response.data;
  },

  // User: Create a new ticket with files (multipart)
  createTicketWithFiles: async (data: CreateTicketRequest, files: File[]): Promise<SupportTicket> => {
    const formData = new FormData();
    formData.append('subject', data.subject);
    formData.append('message', data.message);
    formData.append('priority', data.priority);
    files.forEach((file) => formData.append('files', file));
    const response = await api.post<SupportTicket>('/api/support/tickets/with-files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // User: Get my tickets
  getMyTickets: async (statusFilter?: TicketStatus): Promise<SupportTicket[]> => {
    const params = statusFilter ? `?status_filter=${statusFilter}` : '';
    const response = await api.get<SupportTicket[]>(`/api/support/tickets${params}`);
    return response.data;
  },

  // User: Get single ticket
  getTicket: async (ticketId: number): Promise<SupportTicket> => {
    const response = await api.get<SupportTicket>(`/api/support/tickets/${ticketId}`);
    return response.data;
  },

  // User: Reply to ticket (JSON, no files)
  replyToTicket: async (ticketId: number, data: TicketReplyRequest): Promise<TicketReply> => {
    const response = await api.post<TicketReply>(`/api/support/tickets/${ticketId}/reply`, data);
    return response.data;
  },

  // User: Reply to ticket with files (multipart)
  replyToTicketWithFiles: async (ticketId: number, message: string, files: File[]): Promise<TicketReply> => {
    const formData = new FormData();
    formData.append('message', message);
    files.forEach((file) => formData.append('files', file));
    const response = await api.post<TicketReply>(
      `/api/support/tickets/${ticketId}/reply-with-files`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // User: Upload attachments to existing ticket
  uploadAttachments: async (ticketId: number, files: File[]): Promise<TicketAttachment[]> => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    const response = await api.post<TicketAttachment[]>(
      `/api/support/tickets/${ticketId}/attachments`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // Admin: Get all tickets
  adminGetAllTickets: async (
    statusFilter?: TicketStatus,
    priorityFilter?: TicketPriority
  ): Promise<TicketWithUser[]> => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status_filter', statusFilter);
    if (priorityFilter) params.append('priority_filter', priorityFilter);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const response = await api.get<TicketWithUser[]>(`/api/support/admin/tickets${queryString}`);
    return response.data;
  },

  // Admin: Get ticket detail
  adminGetTicketDetail: async (ticketId: number): Promise<TicketWithUser> => {
    const response = await api.get<TicketWithUser>(`/api/support/admin/tickets/${ticketId}`);
    return response.data;
  },

  // Admin: Respond to ticket (JSON, no files)
  adminRespond: async (ticketId: number, data: TicketReplyRequest): Promise<TicketReply> => {
    const response = await api.post<TicketReply>(`/api/support/admin/tickets/${ticketId}/respond`, data);
    return response.data;
  },

  // Admin: Respond with files (multipart)
  adminRespondWithFiles: async (ticketId: number, message: string, files: File[]): Promise<TicketReply> => {
    const formData = new FormData();
    formData.append('message', message);
    files.forEach((file) => formData.append('files', file));
    const response = await api.post<TicketReply>(
      `/api/support/admin/tickets/${ticketId}/respond-with-files`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // Admin: Update ticket status
  adminUpdateStatus: async (
    ticketId: number,
    data: UpdateTicketStatusRequest
  ): Promise<{ success: boolean; message: string; ticket_id: number; new_status: TicketStatus }> => {
    const response = await api.patch(`/api/support/admin/tickets/${ticketId}/status`, data);
    return response.data;
  },

  // Admin: Get support stats
  adminGetStats: async (): Promise<SupportStats> => {
    const response = await api.get<SupportStats>('/api/support/admin/stats');
    return response.data;
  },

  // Download attachment (authenticated, triggers browser download)
  downloadAttachment: async (attachmentId: number, filename: string): Promise<void> => {
    const response = await api.get(`/api/support/attachments/${attachmentId}`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
