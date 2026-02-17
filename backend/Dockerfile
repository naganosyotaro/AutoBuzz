# Dockerfile

# Python 3.11を使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# エントリーポイントスクリプトをコピーして実行権限を付与
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# アプリケーションを起動 (DB接続待機 -> マイグレーション -> サーバー起動)
CMD ["./entrypoint.sh"]
