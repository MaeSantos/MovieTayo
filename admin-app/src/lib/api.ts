// API client for the MovieTayo admin endpoints.
// Adds the X-Admin-Token header and returns parsed JSON.

const TOKEN_KEY = "movietayo.admin.token";

export function getAdminToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? "";
}

export function setAdminToken(token: string): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Token": getAdminToken(),
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const text = await res.text();
      if (text) detail = text;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export interface TopGenre {
  genre: string;
  count: number;
}

export interface TopMovie {
  title: string;
  saved_count: number;
}

export interface DashboardStats {
  catalog_items: number;
  saved_items: number;
  behavior_events: number;
  reports: number;
  open_reports: number;
  users: number;
  top_genres: TopGenre[];
  top_movies: TopMovie[];
}

export interface ReportRow {
  id: number;
  user_id: string;
  category: string;
  message: string;
  status: "new" | "reviewing" | "resolved" | string;
  created_at: string;
}

export interface UserRow {
  user_id: string;
  saved_count: number;
  behavior_count: number;
  report_count: number;
  top_genres: TopGenre[];
  recent_searches: string[];
}

export interface CatalogRow {
  id: number;
  title: string;
  kind: string;
  genres: string;
  has_image_url: boolean;
  has_poster_data: boolean;
}

export interface BehaviorRow {
  id: number;
  user_id: string;
  interaction_type: string;
  content_id?: string;
  title?: string;
  dwell_time?: number | null;
  context: Record<string, unknown>;
  created_at: string;
}

export const api = {
  async pingAuth(): Promise<DashboardStats> {
    return request<DashboardStats>("/api/admin/stats");
  },
  async stats(): Promise<DashboardStats> {
    return request<DashboardStats>("/api/admin/stats");
  },
  async reports(status?: string): Promise<ReportRow[]> {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<ReportRow[]>(`/api/admin/reports${qs}`);
  },
  async updateReport(id: number, status: string): Promise<void> {
    await request(`/api/admin/reports/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },
  async users(): Promise<UserRow[]> {
    return request<UserRow[]>("/api/admin/users");
  },
  async catalog(query: string): Promise<CatalogRow[]> {
    const qs = query ? `&q=${encodeURIComponent(query)}` : "";
    return request<CatalogRow[]>(`/api/admin/catalog?limit=120${qs}`);
  },
  async behavior(): Promise<BehaviorRow[]> {
    return request<BehaviorRow[]>("/api/admin/behavior?limit=120");
  },
};
