import api from './axios';
import type {
  SupportTicket,
  TicketWithUser,
  TicketReply,
  CreateTicketRequest,
  TicketReplyRequest,
  UpdateTicketStatusRequest,
  SupportStats,
  TicketStatus,
  TicketPriority,
} from '../types/support';

export const supportApi = {
  // User: Create a new ticket
  createTicket: async (data: CreateTicketRequest): Promise<SupportTicket> => {
    const response = await api.post<SupportTicket>('/api/support/tickets', data);
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

  // User: Reply to ticket
  replyToTicket: async (ticketId: number, data: TicketReplyRequest): Promise<TicketReply> => {
    const response = await api.post<TicketReply>(`/api/support/tickets/${ticketId}/reply`, data);
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

  // Admin: Respond to ticket
  adminRespond: async (ticketId: number, data: TicketReplyRequest): Promise<TicketReply> => {
    const response = await api.post<TicketReply>(`/api/support/admin/tickets/${ticketId}/respond`, data);
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
};
