"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function AffiliatePage() {
  const [offers, setOffers] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showOfferModal, setShowOfferModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);

  // Offer form
  const [title, setTitle] = useState("");
  const [affiliateUrl, setAffiliateUrl] = useState("");
  const [genre, setGenre] = useState("");

  // Account form
  const [accPlatform, setAccPlatform] = useState("amazon");
  const [trackingId, setTrackingId] = useState("");

  const load = () => {
    Promise.all([api.getAffiliateOffers(), api.getAffiliateAccounts()])
      .then(([o, a]) => { setOffers(o); setAccounts(a); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreateOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createAffiliateOffer(title, affiliateUrl, genre || undefined);
    setTitle(""); setAffiliateUrl(""); setGenre("");
    setShowOfferModal(false);
    load();
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createAffiliateAccount(accPlatform, trackingId);
    setTrackingId("");
    setShowAccountModal(false);
    load();
  };

  const handleDeleteOffer = async (id: string) => {
    await api.deleteAffiliateOffer(id);
    setOffers(offers.filter((o) => o.id !== id));
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>アフィリエイト管理</h2>
        <p>アフィリエイト案件とアカウントを管理</p>
      </div>

      {/* Accounts */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700 }}>🏦 アフィリエイトアカウント</h3>
          <button className="btn btn-secondary btn-sm" onClick={() => setShowAccountModal(true)}>＋ 追加</button>
        </div>
        {accounts.length === 0 ? (
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>アカウント未登録</p>
        ) : (
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            {accounts.map((a) => (
              <span className="badge badge-success" key={a.id} style={{ padding: "6px 14px", fontSize: 13 }}>
                {a.platform} ({a.tracking_id})
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Offers */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700 }}>📋 アフィリエイト案件</h3>
          <button className="btn btn-primary btn-sm" onClick={() => setShowOfferModal(true)}>＋ 案件追加</button>
        </div>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}><div className="loading-spinner" /></div>
        ) : offers.length === 0 ? (
          <div className="empty-state">
            <div className="icon">💰</div>
            <h3>案件未登録</h3>
            <p>アフィリエイト案件を追加して投稿に自動挿入</p>
            <button className="btn btn-primary" onClick={() => setShowOfferModal(true)}>案件を追加</button>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr><th>タイトル</th><th>ジャンル</th><th>URL</th><th></th></tr>
              </thead>
              <tbody>
                {offers.map((o) => (
                  <tr key={o.id}>
                    <td style={{ fontWeight: 600 }}>{o.title}</td>
                    <td>{o.genre ? <span className="badge badge-info">{o.genre}</span> : "—"}</td>
                    <td style={{ maxWidth: 240, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 13, color: "var(--text-secondary)" }}>
                      {o.affiliate_url}
                    </td>
                    <td><button className="btn btn-danger btn-sm" onClick={() => handleDeleteOffer(o.id)}>削除</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showOfferModal && (
        <div className="modal-overlay" onClick={() => setShowOfferModal(false)}>
          <div className="modal fade-in" onClick={(e) => e.stopPropagation()}>
            <h3>アフィリエイト案件追加</h3>
            <form onSubmit={handleCreateOffer}>
              <div className="form-group">
                <label className="form-label">タイトル</label>
                <input className="form-input" placeholder="例: おすすめプログラミング教材" value={title} onChange={(e) => setTitle(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">アフィリエイトURL</label>
                <input className="form-input" placeholder="https://..." value={affiliateUrl} onChange={(e) => setAffiliateUrl(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">ジャンル（任意）</label>
                <input className="form-input" placeholder="例: テクノロジー" value={genre} onChange={(e) => setGenre(e.target.value)} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowOfferModal(false)}>キャンセル</button>
                <button type="submit" className="btn btn-primary">追加</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAccountModal && (
        <div className="modal-overlay" onClick={() => setShowAccountModal(false)}>
          <div className="modal fade-in" onClick={(e) => e.stopPropagation()}>
            <h3>アフィリエイトアカウント追加</h3>
            <form onSubmit={handleCreateAccount}>
              <div className="form-group">
                <label className="form-label">プラットフォーム</label>
                <select className="form-input form-select" value={accPlatform} onChange={(e) => setAccPlatform(e.target.value)}>
                  <option value="amazon">Amazon アソシエイト</option>
                  <option value="rakuten">楽天</option>
                  <option value="asp">ASP</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">トラッキングID</label>
                <input className="form-input" placeholder="your-tracking-id" value={trackingId} onChange={(e) => setTrackingId(e.target.value)} required />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAccountModal(false)}>キャンセル</button>
                <button type="submit" className="btn btn-primary">追加</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
