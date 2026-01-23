// Support Ticket Types

export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type TicketPriority = 'low' | 'medium' | 'high';

export interface TicketReply {
  id: number;
  message: string;
  is_admin_reply: boolean;
  user_email: string | null;
  user_name: string | null;
  created_at: string;
}

export interface SupportTicket {
  id: number;
  subject: string;
  message: string;
  status: TicketStatus;
  priority: TicketPriority;
  created_at: string;
  updated_at: string;
  replies: TicketReply[];
}

export interface TicketWithUser extends SupportTicket {
  user_id: number;
  user_email: string;
  user_name: string | null;
  reply_count: number;
}

export interface CreateTicketRequest {
  subject: string;
  message: string;
  priority: TicketPriority;
}

export interface TicketReplyRequest {
  message: string;
}

export interface UpdateTicketStatusRequest {
  status: TicketStatus;
}

export interface SupportStats {
  total_tickets: number;
  open: number;
  in_progress: number;
  resolved: number;
  closed: number;
  high_priority_pending: number;
}
