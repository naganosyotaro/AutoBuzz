"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

interface TrendItem {
  source: string;
  title: string;
  description: string;
  score: number;
  url: string;
  category?: string;
}

interface TrendsData {
  google_trends: TrendItem[];
  news: TrendItem[];
  x_buzz: TrendItem[];
  top_keywords: string[];
}

type Mode = "manual" | "autopilot";

export default function PostsPage() {
  const [mode, setMode] = useState<Mode>("manual");

  // 共通
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 手動モード
  const [generating, setGenerating] = useState(false);
  const [platform, setPlatform] = useState("x");
  const [genre, setGenre] = useState("");
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [trendsLoading, setTrendsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"google" | "news" | "x">("google");

  // 全自動モード
  const [autopilotEnabled, setAutopilotEnabled] = useState(false);
  const [autopilotLoading, setAutopilotLoading] = useState(true);
  const [runningNow, setRunningNow] = useState(false);
  const [runResult, setRunResult] = useState<any>(null);

  const load = () => {
    api.getPosts().then(setPosts).catch(console.error).finally(() => setLoading(false));
  };

  const loadTrends = () => {
    setTrendsLoading(true);
    api.getTrends().then(setTrends).catch(console.error).finally(() => setTrendsLoading(false));
  };

  const loadAutopilotStatus = () => {
    setAutopilotLoading(true);
    api.getAutopilotStatus()
      .then((data: any) => setAutopilotEnabled(data.enabled))
      .catch(console.error)
      .finally(() => setAutopilotLoading(false));
  };

  useEffect(() => {
    load();
    loadTrends();
    loadAutopilotStatus();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generatePost(platform, genre || undefined);
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    await api.deletePost(id);
    setPosts(posts.filter((p) => p.id !== id));
  };

  const handleToggleAutopilot = async () => {
    const next = !autopilotEnabled;
    try {
      await api.toggleAutopilot(next);
      setAutopilotEnabled(next);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunNow = async () => {
    setRunningNow(true);
    setRunResult(null);
    try {
      const result = await api.runAutopilotNow();
      setRunResult(result);
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningNow(false);
    }
  };

  const sourceIcon = (source: string) => {
    switch (source) {
      case "google_trends": return "📈";
      case "news": return "📰";
      case "x": return "𝕏";
      default: return "🔍";
    }
  };

  const currentTrends = activeTab === "google"
    ? trends?.google_trends || []
    : activeTab === "news"
    ? trends?.news || []
    : trends?.x_buzz || [];

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>投稿管理</h2>
        <p>手動で投稿を生成するか、全自動でおまかせできます</p>
      </div>

      {/* ─── モード切替タブ ─── */}
      <div style={{
        display: "flex",
        gap: 0,
        marginBottom: 24,
        borderRadius: 12,
        overflow: "hidden",
        border: "1px solid var(--border)",
      }}>
        <button
          onClick={() => setMode("manual")}
          style={{
            flex: 1,
            padding: "14px 20px",
            border: "none",
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 14,
            transition: "all 0.3s",
            background: mode === "manual"
              ? "linear-gradient(135deg, var(--primary), var(--primary-hover))"
              : "var(--card-bg)",
            color: mode === "manual" ? "#fff" : "var(--text-secondary)",
          }}
        >
          ✋ 手動モード
        </button>
        <button
          onClick={() => setMode("autopilot")}
          style={{
            flex: 1,
            padding: "14px 20px",
            border: "none",
            borderLeft: "1px solid var(--border)",
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 14,
            transition: "all 0.3s",
            background: mode === "autopilot"
              ? "linear-gradient(135deg, #10b981, #059669)"
              : "var(--card-bg)",
            color: mode === "autopilot" ? "#fff" : "var(--text-secondary)",
          }}
        >
          🤖 全自動おまかせ
        </button>
      </div>

      {/* ═══════════ 手動モード ═══════════ */}
      {mode === "manual" && (
        <>
          {/* トレンドセクション */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700 }}>🔥 現在のトレンド</h3>
              <button className="btn btn-secondary btn-sm" onClick={loadTrends} disabled={trendsLoading}>
                {trendsLoading ? <span className="loading-spinner" style={{ width: 14, height: 14 }} /> : "🔄 更新"}
              </button>
            </div>

            {trends?.top_keywords && trends.top_keywords.length > 0 && (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
                {trends.top_keywords.map((kw, i) => (
                  <span key={i} className="badge badge-info" style={{ cursor: "pointer", padding: "6px 12px", fontSize: 12 }}
                    onClick={() => setGenre(kw)} title="クリックでジャンルに設定">
                    🏷️ {kw}
                  </span>
                ))}
              </div>
            )}

            <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
              {([
                { key: "google" as const, label: "📈 Google", count: trends?.google_trends?.length || 0 },
                { key: "news" as const, label: "📰 ニュース", count: trends?.news?.length || 0 },
                { key: "x" as const, label: "𝕏 バズ", count: trends?.x_buzz?.length || 0 },
              ]).map((tab) => (
                <button key={tab.key}
                  className={`btn btn-sm ${activeTab === tab.key ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => setActiveTab(tab.key)} style={{ fontSize: 12, padding: "6px 14px" }}>
                  {tab.label} ({tab.count})
                </button>
              ))}
            </div>

            {trendsLoading ? (
              <div style={{ display: "flex", justifyContent: "center", padding: 30 }}><div className="loading-spinner" /></div>
            ) : currentTrends.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", fontSize: 14, textAlign: "center", padding: 20 }}>データなし</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 300, overflowY: "auto" }}>
                {currentTrends.map((item, idx) => (
                  <div key={idx} style={{
                    display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 14px",
                    borderRadius: 8, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)",
                    cursor: "pointer", transition: "background 0.2s",
                  }} onClick={() => setGenre(item.title)} title="クリックでジャンルに設定">
                    <span style={{ fontSize: 18, flexShrink: 0 }}>{sourceIcon(item.source)}</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 2 }}>{item.title}</div>
                      {item.description && item.description !== item.title && (
                        <div style={{ fontSize: 12, color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {item.description}
                        </div>
                      )}
                    </div>
                    {item.category && <span className="badge badge-warning" style={{ fontSize: 10, padding: "2px 8px", flexShrink: 0 }}>{item.category}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI投稿生成 */}
          <div className="card" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>🤖 AI投稿生成</h3>
            <p style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 16 }}>
              トレンドをクリック→ジャンルに反映。生成時にトレンドが自動分析されます。
            </p>
            <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
              <div className="form-group" style={{ marginBottom: 0, minWidth: 160 }}>
                <label className="form-label">プラットフォーム</label>
                <select className="form-input form-select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
                  <option value="x">𝕏 (Twitter)</option>
                  <option value="threads">Threads</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 0, flex: 1, minWidth: 200 }}>
                <label className="form-label">ジャンル</label>
                <input className="form-input" placeholder="例: テクノロジー" value={genre} onChange={(e) => setGenre(e.target.value)} />
              </div>
              <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
                {generating ? (<><span className="loading-spinner" style={{ width: 14, height: 14, marginRight: 6 }} />分析中...</>) : "✨ 投稿を生成"}
              </button>
            </div>
          </div>
        </>
      )}

      {/* ═══════════ 全自動おまかせモード ═══════════ */}
      {mode === "autopilot" && (
        <>
          {/* ON/OFFトグル */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>🚀 全自動おまかせモード</h3>
                <p style={{ fontSize: 13, color: "var(--text-secondary)", margin: 0 }}>
                  設定したジャンル × 全プラットフォーム（X, Threads）で<br />
                  トレンドを自動調査 → 投稿を自動生成 → スケジュール時刻に自動投稿
                </p>
              </div>
              {autopilotLoading ? (
                <div className="loading-spinner" />
              ) : (
                <button
                  onClick={handleToggleAutopilot}
                  style={{
                    padding: "10px 28px",
                    borderRadius: 30,
                    border: "none",
                    fontWeight: 700,
                    fontSize: 14,
                    cursor: "pointer",
                    transition: "all 0.3s",
                    background: autopilotEnabled
                      ? "linear-gradient(135deg, #10b981, #059669)"
                      : "rgba(255,255,255,0.1)",
                    color: autopilotEnabled ? "#fff" : "var(--text-secondary)",
                    boxShadow: autopilotEnabled ? "0 4px 15px rgba(16,185,129,0.4)" : "none",
                  }}
                >
                  {autopilotEnabled ? "✅ ON" : "OFF"}
                </button>
              )}
            </div>
          </div>

          {/* フロー説明 */}
          <div className="card" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>📋 自動投稿の流れ</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {[
                { step: "1", icon: "🏷️", title: "ジャンル設定", desc: "投稿したいジャンルを設定", link: "/dashboard/genres", linkText: "ジャンル設定へ →" },
                { step: "2", icon: "⏰", title: "スケジュール設定", desc: "投稿する時間と頻度を設定", link: "/dashboard/schedule", linkText: "スケジュール設定へ →" },
                { step: "3", icon: "🔥", title: "トレンド自動調査", desc: "Google Trends・ニュース・Xから自動収集", link: null, linkText: null },
                { step: "4", icon: "✨", title: "AI投稿生成", desc: "各ジャンル × X・Threads で投稿を自動生成", link: null, linkText: null },
                { step: "5", icon: "📮", title: "自動投稿", desc: "スケジュール時刻にSNSへ自動投稿", link: null, linkText: null },
              ].map((item) => (
                <div key={item.step} style={{
                  display: "flex", alignItems: "center", gap: 14,
                  padding: "12px 16px", borderRadius: 10,
                  background: "rgba(255,255,255,0.03)", border: "1px solid var(--border)",
                }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: "50%",
                    background: "linear-gradient(135deg, var(--primary), var(--primary-hover))",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontWeight: 700, fontSize: 14, color: "#fff", flexShrink: 0,
                  }}>{item.step}</div>
                  <span style={{ fontSize: 22, flexShrink: 0 }}>{item.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{item.desc}</div>
                  </div>
                  {item.link && (
                    <Link href={item.link} className="btn btn-secondary btn-sm" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
                      {item.linkText}
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 今すぐ実行ボタン */}
          <div className="card" style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>⚡ 今すぐ実行（テスト）</h3>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
              スケジュールを待たずに、今すぐ全ジャンル×全プラットフォームで投稿を生成します。
            </p>
            <button className="btn btn-primary" onClick={handleRunNow} disabled={runningNow} style={{ marginBottom: 12 }}>
              {runningNow ? (
                <><span className="loading-spinner" style={{ width: 14, height: 14, marginRight: 6 }} />トレンド分析＆投稿生成中...</>
              ) : "🚀 今すぐ全自動投稿を実行"}
            </button>
            {runResult && (
              <div style={{
                padding: 16, borderRadius: 10, background: "rgba(16,185,129,0.1)",
                border: "1px solid rgba(16,185,129,0.3)",
              }}>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8, color: "#10b981" }}>
                  ✅ {runResult.message}
                </div>
                {runResult.results && runResult.results.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {runResult.results.map((r: any, i: number) => (
                      <div key={i} style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                        <span className="badge badge-info" style={{ marginRight: 8, fontSize: 10 }}>
                          {r.platform === "x" ? "𝕏" : "Threads"}
                        </span>
                        {r.genre && <span className="badge badge-warning" style={{ marginRight: 8, fontSize: 10 }}>{r.genre}</span>}
                        <span className={`badge ${r.status === "posted" ? "badge-success" : r.status === "error" ? "badge-danger" : "badge-warning"}`} style={{ fontSize: 10 }}>
                          {r.status === "posted" ? "投稿済み" : r.status === "error" ? "エラー" : "下書き"}
                        </span>
                        <span style={{ marginLeft: 8 }}>{r.content}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* ─── 投稿一覧（共通） ─── */}
      <div className="card">
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>投稿一覧</h3>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}><div className="loading-spinner" /></div>
        ) : posts.length === 0 ? (
          <div className="empty-state">
            <div className="icon">📝</div>
            <h3>投稿がありません</h3>
            <p>{mode === "manual" ? "トレンドを確認してAI投稿を生成しましょう" : "全自動モードをONにしてスケジュールを設定しましょう"}</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>SNS</th>
                  <th>内容</th>
                  <th>ステータス</th>
                  <th>作成日</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {posts.map((post) => (
                  <tr key={post.id}>
                    <td><span className="badge badge-info">{post.platform === "x" ? "𝕏" : "Threads"}</span></td>
                    <td style={{ maxWidth: 400 }}>
                      <div style={{ whiteSpace: "pre-wrap", fontSize: 13, lineHeight: 1.5 }}>{post.content}</div>
                    </td>
                    <td>
                      <span className={`badge ${post.status === "posted" ? "badge-success" : post.status === "pending" ? "badge-info" : "badge-warning"}`}>
                        {post.status === "posted" ? "投稿済み" : post.status === "pending" ? "予約中" : "下書き"}
                      </span>
                    </td>
                    <td style={{ fontSize: 13, color: "var(--text-secondary)", whiteSpace: "nowrap" }}>
                      {new Date(post.created_at).toLocaleString("ja-JP")}
                    </td>
                    <td><button className="btn btn-danger btn-sm" onClick={() => handleDelete(post.id)}>削除</button></td>
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
