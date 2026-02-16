"use client";

export default function SettingsPage() {
  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>設定</h2>
        <p>アカウントとプランの管理</p>
      </div>

      <div className="card-grid">
        <div className="card">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>📋 プラン</h3>
          <div style={{ marginBottom: 16 }}>
            <span className="badge badge-success" style={{ padding: "8px 16px", fontSize: 14 }}>Free プラン</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.7 }}>
            現在のプラン: 1日1投稿まで
          </p>
          <div style={{ marginTop: 20 }}>
            <div className="card" style={{ background: "rgba(99, 102, 241, 0.08)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>🚀 Basic プラン</div>
              <div style={{ fontSize: 24, fontWeight: 800, marginBottom: 4 }}>¥980<span style={{ fontSize: 13, fontWeight: 400, color: "var(--text-secondary)" }}>/月</span></div>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 12 }}>無制限投稿、全機能解放</p>
              <button className="btn btn-primary btn-sm">アップグレード（準備中）</button>
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div className="card" style={{ background: "rgba(168, 85, 247, 0.08)", border: "1px solid rgba(168, 85, 247, 0.2)" }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>💎 Pro プラン</div>
              <div style={{ fontSize: 24, fontWeight: 800, marginBottom: 4 }}>¥2,980<span style={{ fontSize: 13, fontWeight: 400, color: "var(--text-secondary)" }}>/月</span></div>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 12 }}>優先サポート、APIアクセス、高度な分析</p>
              <button className="btn btn-primary btn-sm">アップグレード（準備中）</button>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>🔑 API設定</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.7 }}>
            外部サービスのAPI設定はサーバー側の <code style={{ background: "var(--bg-card)", padding: "2px 6px", borderRadius: 4, fontSize: 13 }}>.env</code> ファイルで管理されます。
          </p>
          <div style={{ marginTop: 16 }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {[
                { name: "OpenAI API", status: "設定が必要" },
                { name: "X (Twitter) API", status: "設定が必要" },
                { name: "Threads API", status: "設定が必要" },
                { name: "News API", status: "設定が必要" },
              ].map((item) => (
                <div key={item.name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ fontSize: 14 }}>{item.name}</span>
                  <span className="badge badge-warning">{item.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
