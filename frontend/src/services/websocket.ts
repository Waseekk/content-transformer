/**
 * WebSocket Service for Real-time Updates
 */

import { io, Socket } from 'socket.io-client';
import { useAppStore } from '../store/useAppStore';

const WS_URL = import.meta.env.VITE_API_URL?.replace('/api', '') ?? '';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect() {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', () => {
      // Connection lost - will auto-reconnect
    });

    // Scraper updates
    this.socket.on('scraper_progress', (data) => {
      useAppStore.getState().setScraperStatus(data);
    });

    this.socket.on('scraper_complete', (data) => {
      useAppStore.getState().setScraperStatus(data);
    });

    // Scheduler updates
    this.socket.on('scheduler_status', (data) => {
      useAppStore.getState().setSchedulerStatus(data);
    });

    this.socket.on('connect_error', () => {
      this.reconnectAttempts++;
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data?: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }
}

export const wsService = new WebSocketService();
