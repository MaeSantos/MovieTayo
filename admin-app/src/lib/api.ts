const API_BASE = (import.meta.env.VITE_API_BASE as string) || '/api';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface AdminStats {
  catalog_items: number;
  users: number;
  saved_items: number;
  open_reports: number;
  behavior_events: number;
  reports: number;
  top_genres: Array<{ genre: string; count: number }>;
  top_movies: Array<{ title: string; saved_count: number }>;
}

export interface Report {
  id: number;
  user_id: string;
  report_type: string;
  status: 'new' | 'reviewing' | 'resolved';
  message: string;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  is_active: boolean;
}

export interface CatalogItem {
  id: number;
  title: string;
  content_type: string;
  year: number;
  genres: Array<{ genre: string }>;
  has_poster: boolean;
}

export interface BehaviorEvent {
  id: number;
  user_id: string;
  action_type: string;
  content_id: number;
  timestamp: string;
  context?: Record<string, unknown>;
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('movietayo.admin.token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('movietayo.admin.token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('movietayo.admin.token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['X-Admin-Token'] = this.token;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text().catch(() => 'Unknown error');
      throw new Error(error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getStats(): Promise<AdminStats> {
    return this.request<AdminStats>('/admin/stats');
  }

  async getReports(status?: string): Promise<{ reports: Report[] }> {
    const params = status ? `?status=${status}` : '';
    return this.request<{ reports: Report[] }>(`/admin/reports${params}`);
  }

  async getUsers(): Promise<{ users: User[] }> {
    return this.request<{ users: User[] }>('/admin/users');
  }

  async getCatalog(query?: string): Promise<{ items: CatalogItem[] }> {
    const params = query ? `?q=${encodeURIComponent(query)}` : '';
    return this.request<{ items: CatalogItem[] }>(`/admin/catalog${params}`);
  }

  async getBehavior(): Promise<{ events: BehaviorEvent[] }> {
    return this.request<{ events: BehaviorEvent[] }>('/admin/behavior');
  }

  async updateReportStatus(
    reportId: number,
    status: 'new' | 'reviewing' | 'resolved'
  ): Promise<void> {
    return this.request(`/admin/reports/${reportId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }
}

export const api = new ApiClient();
