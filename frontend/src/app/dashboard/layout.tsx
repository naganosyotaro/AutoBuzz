"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, ReactNode } from "react";
import Link from "next/link";

const navItems = [
  { href: "/dashboard", icon: "📊", label: "ダッシュボード", section: "メイン" },
  { href: "/dashboard/posts", icon: "✍️", label: "投稿管理", section: "メイン" },
  { href: "/dashboard/schedule", icon: "⏰", label: "スケジュール", section: "メイン" },
  { href: "/dashboard/accounts", icon: "🔗", label: "SNSアカウント", section: "連携" },
  { href: "/dashboard/genres", icon: "🏷️", label: "ジャンル設定", section: "連携" },
  { href: "/dashboard/affiliate", icon: "💰", label: "アフィリエイト", section: "収益" },
  { href: "/dashboard/revenue", icon: "📈", label: "収益レポート", section: "収益" },
  { href: "/dashboard/settings", icon: "⚙️", label: "設定", section: "その他" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" style={{ width: 32, height: 32 }} />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  const sections = Array.from(new Set(navItems.map((i) => i.section)));

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>⚡ AutoBuzz</h1>
          <span>SNS自動投稿 & 収益化</span>
        </div>
        <nav className="sidebar-nav">
          {sections.map((section) => (
            <div className="nav-section" key={section}>
              <div className="nav-section-label">{section}</div>
              {navItems
                .filter((i) => i.section === section)
                .map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`nav-item ${pathname === item.href ? "active" : ""}`}
                  >
                    <span className="icon">{item.icon}</span>
                    {item.label}
                  </Link>
                ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="nav-item" onClick={logout} style={{ width: "100%" }}>
            <span className="icon">🚪</span>
            ログアウト
          </button>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
