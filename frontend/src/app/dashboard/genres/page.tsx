"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function GenresPage() {
  const [genres, setGenres] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [keywords, setKeywords] = useState("");

  const load = () => {
    api.getGenres().then(setGenres).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const kws = keywords.split(",").map((k) => k.trim()).filter(Boolean);
    await api.createGenre(name, kws);
    setName("");
    setKeywords("");
    load();
  };

  const handleDelete = async (id: string) => {
    await api.deleteGenre(id);
    setGenres(genres.filter((g) => g.id !== id));
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>ジャンル設定</h2>
        <p>投稿するジャンルとキーワードを管理</p>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>🏷️ ジャンル追加</h3>
        <form onSubmit={handleCreate} style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="form-group" style={{ marginBottom: 0, minWidth: 180 }}>
            <label className="form-label">ジャンル名</label>
            <input className="form-input" placeholder="例: テクノロジー" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="form-group" style={{ marginBottom: 0, flex: 1, minWidth: 240 }}>
            <label className="form-label">キーワード（カンマ区切り）</label>
            <input className="form-input" placeholder="例: AI, プログラミング, 自動化" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary">追加</button>
        </form>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}><div className="loading-spinner" /></div>
        ) : genres.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🏷️</div>
            <h3>ジャンル未設定</h3>
            <p>投稿のジャンルを追加してAIの精度を向上させましょう</p>
          </div>
        ) : (
          <div className="card-grid">
            {genres.map((g) => (
              <div className="card" key={g.id}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>{g.genre_name}</div>
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {g.keywords.map((kw: string) => (
                        <span className="badge badge-info" key={kw}>{kw}</span>
                      ))}
                    </div>
                  </div>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(g.id)}>削除</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
