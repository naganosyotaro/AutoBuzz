"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [platform, setPlatform] = useState("x");
  const [accessToken, setAccessToken] = useState("");
  const [accessTokenSecret, setAccessTokenSecret] = useState("");
  const [accountName, setAccountName] = useState("");

  const load = () => {
    api.getSnsAccounts().then(setAccounts).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.connectSns(platform, accessToken, accessTokenSecret || undefined, accountName || undefined);
    setShowModal(false);
    setAccessToken("");
    setAccessTokenSecret("");
    setAccountName("");
    load();
  };

  const handleDelete = async (id: string) => {
    await api.deleteSnsAccount(id);
    setAccounts(accounts.filter((a) => a.id !== id));
  };

  return (
    <div className="fade-in">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>SNSアカウント</h2>
          <p>投稿先のSNSアカウントを管理</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>＋ アカウント追加</button>
      </div>

      {loading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: 60 }}><div className="loading-spinner" style={{ width: 32, height: 32 }} /></div>
      ) : accounts.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="icon">🔗</div>
            <h3>アカウント未連携</h3>
            <p>XまたはThreadsのアカウントを連携しましょう</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>アカウントを追加</button>
          </div>
        </div>
      ) : (
        <div className="card-grid">
          {accounts.map((acc) => (
            <div className="card" key={acc.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
                    {acc.platform === "x" ? "𝕏 Twitter" : "Threads"}
                  </div>
                  {acc.account_name && (
                    <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 4 }}>
                      @{acc.account_name}
                    </div>
                  )}
                  <span className="badge badge-success">連携済み</span>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(acc.id)}>解除</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal fade-in" onClick={(e) => e.stopPropagation()}>
            <h3>SNSアカウント連携</h3>
            <form onSubmit={handleConnect}>
              <div className="form-group">
                <label className="form-label">プラットフォーム</label>
                <select className="form-input form-select" value={platform} onChange={(e) => setPlatform(e.target.value)}>
                  <option value="x">𝕏 (Twitter)</option>
                  <option value="threads">Threads</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">アカウント名（任意）</label>
                <input
                  className="form-input"
                  placeholder="例: @your_account"
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Access Token</label>
                <input
                  className="form-input"
                  placeholder="OAuth Access Token"
                  value={accessToken}
                  onChange={(e) => setAccessToken(e.target.value)}
                  required
                />
              </div>

              {platform === "x" && (
                <div className="form-group">
                  <label className="form-label">Access Token Secret <span style={{ color: "var(--accent)", fontSize: 12 }}>※ X投稿に必須</span></label>
                  <input
                    className="form-input"
                    placeholder="OAuth Access Token Secret"
                    value={accessTokenSecret}
                    onChange={(e) => setAccessTokenSecret(e.target.value)}
                    required
                  />
                  <p style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 6 }}>
                    X Developer Portalの「Keys and Tokens」から取得できます。<br />
                    .envのX_API_KEY / X_API_SECRET も設定が必要です。
                  </p>
                </div>
              )}

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>キャンセル</button>
                <button type="submit" className="btn btn-primary">連携する</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
