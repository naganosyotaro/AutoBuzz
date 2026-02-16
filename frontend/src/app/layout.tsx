import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "AutoBuzz - SNS自動投稿＆アフィリエイト収益化SaaS",
  description: "XおよびThreadsへの投稿を完全自動化し、アフィリエイトリンクを自動挿入してSNS運用を収益化するSaaS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
