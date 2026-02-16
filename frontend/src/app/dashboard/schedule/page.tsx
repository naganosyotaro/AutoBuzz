"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SchedulePage() {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [time, setTime] = useState("09:00");
  const [frequency, setFrequency] = useState("daily");

  const load = () => {
    api.getSchedules().then(setSchedules).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createSchedule(time, frequency);
    load();
  };

  const handleDelete = async (id: string) => {
    await api.deleteSchedule(id);
    setSchedules(schedules.filter((s) => s.id !== id));
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>スケジュール設定</h2>
        <p>投稿する時間と頻度を設定</p>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>⏰ 新規スケジュール</h3>
        <form onSubmit={handleCreate} style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">投稿時間</label>
            <input type="time" className="form-input" value={time} onChange={(e) => setTime(e.target.value)} />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">頻度</label>
            <select className="form-input form-select" value={frequency} onChange={(e) => setFrequency(e.target.value)}>
              <option value="daily">毎日</option>
              <option value="weekdays">平日のみ</option>
              <option value="weekends">週末のみ</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">追加</button>
        </form>
      </div>

      <div className="card">
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>設定済みスケジュール</h3>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}><div className="loading-spinner" /></div>
        ) : schedules.length === 0 ? (
          <div className="empty-state">
            <div className="icon">📅</div>
            <h3>スケジュール未設定</h3>
            <p>投稿する時間を追加しましょう</p>
          </div>
        ) : (
          <div className="card-grid">
            {schedules.map((s) => (
              <div className="card" key={s.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 24, fontWeight: 700 }}>{s.time}</div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                    {s.frequency === "daily" ? "毎日" : s.frequency === "weekdays" ? "平日" : "週末"}
                  </div>
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(s.id)}>削除</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
