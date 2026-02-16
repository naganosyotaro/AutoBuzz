"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function RevenuePage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAffiliateStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <div className="loading-spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  const s = stats || { total_clicks: 0, total_revenue: 0, ctr: 0, offers: [] };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>収益レポート</h2>
        <p>アフィリエイト収益の状況を確認</p>
      </div>

      <div className="card-grid">
        <div className="card stat-card">
          <div className="stat-label">総クリック数</div>
          <div className="stat-value">{s.total_clicks.toLocaleString()}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">累計収益</div>
          <div className="stat-value">¥{s.total_revenue.toLocaleString()}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">CTR</div>
          <div className="stat-value">{(s.ctr * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>案件別パフォーマンス</h3>
        {s.offers.length === 0 ? (
          <div className="empty-state">
            <div className="icon">📊</div>
            <h3>データなし</h3>
            <p>アフィリエイト案件を追加すると、ここにレポートが表示されます</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr><th>案件</th><th>ジャンル</th><th>URL</th></tr>
              </thead>
              <tbody>
                {s.offers.map((o: any) => (
                  <tr key={o.id}>
                    <td style={{ fontWeight: 600 }}>{o.title}</td>
                    <td>{o.genre ? <span className="badge badge-info">{o.genre}</span> : "—"}</td>
                    <td style={{ fontSize: 13, color: "var(--text-secondary)" }}>{o.affiliate_url}</td>
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
