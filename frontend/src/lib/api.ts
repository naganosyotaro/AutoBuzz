const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem("autobuzz_token", token);
    } else {
      localStorage.removeItem("autobuzz_token");
    }
  }

  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("autobuzz_token");
    }
    return this.token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "エラーが発生しました" }));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }

    if (res.status === 204) return {} as T;
    return res.json();
  }

  // Auth
  async register(email: string, password: string) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  logout() {
    this.setToken(null);
  }

  // SNS Accounts
  async getSnsAccounts() {
    return this.request<any[]>("/api/sns/accounts");
  }

  async connectSns(platform: string, accessToken: string, accessTokenSecret?: string, accountName?: string) {
    return this.request(`/api/sns/connect/${platform}`, {
      method: "POST",
      body: JSON.stringify({
        platform,
        access_token: accessToken,
        access_token_secret: accessTokenSecret || null,
        account_name: accountName || null,
      }),
    });
  }

  async deleteSnsAccount(id: string) {
    return this.request(`/api/sns/accounts/${id}`, { method: "DELETE" });
  }

  // Genres
  async getGenres() {
    return this.request<any[]>("/api/genres/");
  }

  async createGenre(genreName: string, keywords: string[]) {
    return this.request("/api/genres/", {
      method: "POST",
      body: JSON.stringify({ genre_name: genreName, keywords }),
    });
  }

  async deleteGenre(id: string) {
    return this.request(`/api/genres/${id}`, { method: "DELETE" });
  }

  // Posts
  async getPosts() {
    return this.request<any[]>("/api/posts/");
  }

  async generatePost(platform: string, genre?: string) {
    return this.request("/api/posts/generate", {
      method: "POST",
      body: JSON.stringify({ platform, genre }),
    });
  }

  async deletePost(id: string) {
    return this.request(`/api/posts/${id}`, { method: "DELETE" });
  }

  // Schedules
  async getSchedules() {
    return this.request<any[]>("/api/schedules/");
  }

  async createSchedule(time: string, frequency: string) {
    return this.request("/api/schedules/", {
      method: "POST",
      body: JSON.stringify({ time, frequency }),
    });
  }

  async deleteSchedule(id: string) {
    return this.request(`/api/schedules/${id}`, { method: "DELETE" });
  }

  // Affiliate
  async getAffiliateAccounts() {
    return this.request<any[]>("/api/affiliate/accounts");
  }

  async createAffiliateAccount(platform: string, trackingId: string) {
    return this.request("/api/affiliate/accounts", {
      method: "POST",
      body: JSON.stringify({ platform, tracking_id: trackingId }),
    });
  }

  async getAffiliateOffers() {
    return this.request<any[]>("/api/affiliate/offers");
  }

  async createAffiliateOffer(title: string, affiliateUrl: string, genre?: string) {
    return this.request("/api/affiliate/offers", {
      method: "POST",
      body: JSON.stringify({ title, affiliate_url: affiliateUrl, genre }),
    });
  }

  async deleteAffiliateOffer(id: string) {
    return this.request(`/api/affiliate/offers/${id}`, { method: "DELETE" });
  }

  async getAffiliateStats() {
    return this.request<any>("/api/affiliate/stats");
  }

  // Trends
  async getTrends() {
    return this.request<any>("/api/posts/trends");
  }

  // Autopilot
  async getAutopilotStatus() {
    return this.request<any>("/api/autopilot/status");
  }

  async toggleAutopilot(enabled: boolean) {
    return this.request<any>("/api/autopilot/toggle", {
      method: "POST",
      body: JSON.stringify({ enabled }),
    });
  }

  async runAutopilotNow() {
    return this.request<any>("/api/autopilot/run-now", {
      method: "POST",
    });
  }

  // Dashboard
  async getDashboardStats() {
    return this.request<any>("/api/dashboard/stats");
  }

  // Short Links
  async createShortLink(originalUrl: string) {
    return this.request("/api/links/", {
      method: "POST",
      body: JSON.stringify({ original_url: originalUrl }),
    });
  }
}

export const api = new ApiClient();
