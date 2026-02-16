import asyncio
import logging
from typing import List, Optional
from app.config import settings
import httpx

logger = logging.getLogger(__name__)

# ─── Google Trends（pytrends）─────────────────────────────
async def collect_google_trends(geo: str = "JP", count: int = 20) -> List[dict]:
    """Google Trendsからリアルタイムトレンドワードを取得（APIキー不要）"""
    try:
        from pytrends.request import TrendReq

        def _fetch():
            pytrends = TrendReq(hl="ja-JP", tz=540)
            df = pytrends.trending_searches(pn="japan")
            items = []
            for i, row in df.head(count).iterrows():
                items.append({
                    "source": "google_trends",
                    "title": str(row[0]),
                    "description": f"Google Trendsで急上昇中: {row[0]}",
                    "score": float(count - i),
                    "url": f"https://trends.google.co.jp/trending?geo=JP",
                })
            return items

        return await asyncio.to_thread(_fetch)
    except Exception as e:
        logger.warning(f"Google Trends取得失敗: {e}")
        return _mock_google_trends()


# ─── RSSニュースフィード（APIキー不要）─────────────────────
async def collect_rss_news(max_items: int = 15) -> List[dict]:
    """複数のRSSフィードからトレンドニュースを取得"""
    feeds = [
        ("https://news.yahoo.co.jp/rss/topics/it.xml", "IT・テクノロジー"),
        ("https://news.yahoo.co.jp/rss/topics/business.xml", "ビジネス"),
        ("https://news.yahoo.co.jp/rss/topics/entertainment.xml", "エンタメ"),
        ("https://news.yahoo.co.jp/rss/topics/domestic.xml", "国内"),
        ("https://b.hatena.ne.jp/hotentry/it.rss", "はてブ IT"),
    ]
    try:
        import feedparser

        def _fetch_all():
            items = []
            for url, category in feeds:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:3]:
                        items.append({
                            "source": "news",
                            "title": entry.get("title", ""),
                            "description": entry.get("summary", entry.get("description", ""))[:200],
                            "score": 1.0,
                            "url": entry.get("link", ""),
                            "category": category,
                        })
                except Exception:
                    continue
            return items[:max_items]

        return await asyncio.to_thread(_fetch_all)
    except Exception as e:
        logger.warning(f"RSSフィード取得失敗: {e}")
        return _mock_news()


# ─── X API バズ投稿取得 ─────────────────────────────────
async def collect_buzz_from_x(keywords: Optional[List[str]] = None, max_results: int = 10) -> List[dict]:
    """X APIからバズ投稿を取得する。APIキー未設定時はモック"""
    if not settings.X_BEARER_TOKEN:
        return _mock_buzz_posts()

    query_parts = keywords or ["話題", "バズ"]
    query = " OR ".join(query_parts) + " lang:ja -is:retweet"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {settings.X_BEARER_TOKEN}"},
                params={
                    "query": query,
                    "max_results": max_results,
                    "tweet.fields": "public_metrics,created_at",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json().get("data", [])
            return [
                {
                    "source": "x",
                    "title": tweet.get("text", "")[:60],
                    "description": tweet.get("text", ""),
                    "score": _calc_score(tweet.get("public_metrics", {})),
                    "url": "",
                }
                for tweet in data
            ]
    except Exception as e:
        logger.warning(f"X API取得失敗: {e}")
        return _mock_buzz_posts()


# ─── 統合収集メソッド ────────────────────────────────────
async def collect_all_trends(keywords: Optional[List[str]] = None) -> dict:
    """全ソースからトレンドを収集して統合する"""
    google, rss, x_buzz = await asyncio.gather(
        collect_google_trends(),
        collect_rss_news(),
        collect_buzz_from_x(keywords),
        return_exceptions=True,
    )

    # エラーの場合は空リストに
    if isinstance(google, Exception):
        google = _mock_google_trends()
    if isinstance(rss, Exception):
        rss = _mock_news()
    if isinstance(x_buzz, Exception):
        x_buzz = _mock_buzz_posts()

    all_items = list(google) + list(rss) + list(x_buzz)
    all_items.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {
        "google_trends": list(google),
        "news": list(rss),
        "x_buzz": list(x_buzz),
        "all": all_items[:30],
        "top_keywords": _extract_keywords(all_items),
    }


def _extract_keywords(items: list, top_n: int = 10) -> List[str]:
    """トレンドアイテムからキーワードを抽出"""
    keywords = []
    for item in items:
        title = item.get("title", "")
        if title and len(title) > 1:
            keywords.append(title)
    # 重複排除しつつ順序保持
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    return unique[:top_n]


# ─── ユーティリティ ──────────────────────────────────────
def _calc_score(metrics: dict) -> float:
    likes = metrics.get("like_count", 0)
    retweets = metrics.get("retweet_count", 0)
    replies = metrics.get("reply_count", 0)
    return float(likes * 1.0 + retweets * 2.0 + replies * 0.5)


# ─── モックデータ ────────────────────────────────────────
def _mock_google_trends() -> List[dict]:
    return [
        {"source": "google_trends", "title": "AI エージェント", "description": "Google Trendsで急上昇中: AI エージェント", "score": 10.0, "url": ""},
        {"source": "google_trends", "title": "生成AI 最新", "description": "Google Trendsで急上昇中: 生成AI 最新", "score": 9.0, "url": ""},
        {"source": "google_trends", "title": "ChatGPT 新機能", "description": "Google Trendsで急上昇中: ChatGPT 新機能", "score": 8.0, "url": ""},
        {"source": "google_trends", "title": "副業 2026", "description": "Google Trendsで急上昇中: 副業 2026", "score": 7.0, "url": ""},
        {"source": "google_trends", "title": "プログラミング 独学", "description": "Google Trendsで急上昇中: プログラミング 独学", "score": 6.0, "url": ""},
    ]


def _mock_news() -> List[dict]:
    return [
        {"source": "news", "title": "AI技術の最新動向：2026年の注目ポイント", "description": "人工知能技術が急速に進化し、さまざまな産業に影響を与え始めている。", "score": 1.0, "url": "", "category": "IT"},
        {"source": "news", "title": "SNS収益化の新トレンド", "description": "個人のSNS発信から収益を上げる新しい方法が注目されている。", "score": 1.0, "url": "", "category": "ビジネス"},
        {"source": "news", "title": "リモートワーク最新事情", "description": "働き方改革が進み、リモートワークの形態がさらに多様化している。", "score": 1.0, "url": "", "category": "ビジネス"},
    ]


def _mock_buzz_posts() -> List[dict]:
    return [
        {"source": "x", "title": "【話題】AIの使い方を変えるツールが登場", "description": "【話題】AIの使い方を変えるツールが登場！これは本当にすごい。仕事が3倍速になった #AI #効率化 #テック", "score": 150.0, "url": ""},
        {"source": "x", "title": "今日バズってる投稿からわかること", "description": "今日バズってる投稿からわかること：結局、共感×具体性×タイミングが全て。#マーケティング #SNS運用", "score": 120.0, "url": ""},
        {"source": "x", "title": "副業で月10万稼ぐリアルな方法", "description": "副業で月10万稼ぐリアルな方法をまとめました。実際にやってみた結果を公開 #副業 #収入UP", "score": 100.0, "url": ""},
    ]
