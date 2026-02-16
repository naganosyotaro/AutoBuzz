# AutoBuzz 🚀

SNS自動投稿＆アフィリエイト収益化SaaS

## 機能

- 🔥 **トレンド自動調査** — Google Trends・RSS・Xから収集
- 🤖 **AI投稿生成** — OpenAI連携 or テンプレート生成
- ✋ **手動モード** — トレンドを確認して投稿を作成
- 🚀 **全自動おまかせモード** — ジャンル×全SNSで自動投稿
- 📊 **アフィリエイト管理** — 収益トラッキング・短縮URL
- 🔐 **JWT認証** — 安全なユーザー管理

## 技術スタック

| 部分 | 技術 |
|---|---|
| フロントエンド | Next.js 16 / TypeScript |
| バックエンド | FastAPI / SQLAlchemy / SQLite |
| AI | OpenAI API |
| SNS連携 | tweepy (X) / Threads API |

## セットアップ

### バックエンド

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### 環境変数

`.env.example` を `.env` にコピーして設定してください。

## ライセンス

MIT
