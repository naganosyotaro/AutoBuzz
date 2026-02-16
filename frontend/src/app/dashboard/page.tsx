"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Stats {
  total_posts: number;
  total_clicks: number;
  total_revenue: number;
  ctr: number;
  recent_posts: any[];
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <div className="loading-spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  const s = stats || { total_posts: 0, total_clicks: 0, total_revenue: 0, ctr: 0, recent_posts: [] };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>ダッシュボード</h2>
        <p>AutoBuzz の運用状況を一目で確認</p>
      </div>

      <div className="card-grid">
        <div className="card stat-card">
          <div className="stat-label">総投稿数</div>
          <div className="stat-value">{s.total_posts.toLocaleString()}</div>
          <div className="stat-change">自動投稿稼働中</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">クリック数</div>
          <div className="stat-value">{s.total_clicks.toLocaleString()}</div>
          <div className="stat-change">アフィリエイトリンク経由</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">収益</div>
          <div className="stat-value">¥{s.total_revenue.toLocaleString()}</div>
          <div className="stat-change">累計収益</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">CTR</div>
          <div className="stat-value">{(s.ctr * 100).toFixed(1)}%</div>
          <div className="stat-change">クリック率</div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>最近の投稿</h3>
        {s.recent_posts.length === 0 ? (
          <div className="empty-state">
            <div className="icon">✍️</div>
            <h3>まだ投稿がありません</h3>
            <p>投稿管理から最初の投稿を生成しましょう</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>プラットフォーム</th>
                  <th>内容</th>
                  <th>ステータス</th>
                  <th>投稿日時</th>
                </tr>
              </thead>
              <tbody>
                {s.recent_posts.map((post: any) => (
                  <tr key={post.id}>
                    <td>
                      <span className="badge badge-info">
                        {post.platform === "x" ? "𝕏" : "Threads"}
                      </span>
                    </td>
                    <td style={{ maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {post.content}
                    </td>
                    <td>
                      <span className={`badge ${post.status === "posted" ? "badge-success" : "badge-warning"}`}>
                        {post.status === "posted" ? "投稿済み" : post.status === "draft" ? "下書き" : post.status}
                      </span>
                    </td>
                    <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                      {post.posted_at ? new Date(post.posted_at).toLocaleString("ja-JP") : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
