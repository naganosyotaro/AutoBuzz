import random
from typing import Optional, List
from app.config import settings

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


async def generate_post_content(
    genre: Optional[str] = None,
    platform: str = "x",
    trend_data: Optional[dict] = None,
) -> str:
    """
    トレンドデータを活用してSNS投稿を生成する。
    - OpenAI APIキー設定時: トレンドデータをコンテキストとしてAIが生成
    - 未設定時: トレンドデータを使ったテンプレート生成
    """
    if not settings.OPENAI_API_KEY or AsyncOpenAI is None:
        return _template_generate(genre, platform, trend_data)

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    platform_name = "X (Twitter)" if platform == "x" else "Threads"
    max_chars = 280 if platform == "x" else 500

    # トレンドコンテキストを構築
    trend_context = _build_trend_context(trend_data, genre)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    f"あなたは{platform_name}でバズる投稿を作成するプロのSNSコピーライターです。\n"
                    f"以下の現在のトレンドデータを参考にして、バズる投稿を1つ生成してください。\n\n"
                    f"【現在のトレンド情報】\n{trend_context}\n\n"
                    f"【投稿ルール】\n"
                    f"- {max_chars}文字以内\n"
                    f"- トレンドに乗った内容にする\n"
                    f"- 共感を呼ぶ・役に立つ・意外性のある内容にする\n"
                    f"- エンゲージメントが高くなるような文体\n"
                    f"- ハッシュタグを2-3個含める\n"
                    f"- 投稿文のみを出力し、説明は不要"
                ),
            },
            {"role": "user", "content": "今のトレンドに基づいてバズる投稿を1つ生成して"},
        ],
        max_tokens=400,
        temperature=0.9,
    )

    return response.choices[0].message.content.strip()


def _build_trend_context(trend_data: Optional[dict], genre: Optional[str]) -> str:
    """トレンドデータからAIに渡すコンテキスト文を構築"""
    if not trend_data:
        return f"ジャンル: {genre or 'テクノロジー'}（トレンドデータなし）"

    parts = []

    # Google Trends
    google = trend_data.get("google_trends", [])
    if google:
        keywords = [item["title"] for item in google[:8]]
        parts.append(f"■ Google急上昇ワード: {', '.join(keywords)}")

    # ニュース
    news = trend_data.get("news", [])
    if news:
        headlines = [f"・{item['title']}" for item in news[:5]]
        parts.append(f"■ 最新ニュース:\n" + "\n".join(headlines))

    # X バズ投稿
    x_buzz = trend_data.get("x_buzz", [])
    if x_buzz:
        buzz_texts = [f"・{item['description'][:80]}" for item in x_buzz[:3]]
        parts.append(f"■ Xでバズっている投稿:\n" + "\n".join(buzz_texts))

    if genre:
        parts.append(f"■ 指定ジャンル: {genre}")

    return "\n\n".join(parts) if parts else f"ジャンル: {genre or 'テクノロジー'}"


def _template_generate(
    genre: Optional[str] = None,
    platform: str = "x",
    trend_data: Optional[dict] = None,
) -> str:
    """OpenAI未設定時：トレンドデータを使ったテンプレート生成"""

    # トレンドからキーワードを取得
    trend_keywords = []
    trend_headlines = []

    if trend_data:
        trend_keywords = trend_data.get("top_keywords", [])[:5]

        for item in trend_data.get("news", []):
            if item.get("title"):
                trend_headlines.append(item["title"])

        for item in trend_data.get("google_trends", []):
            if item.get("title"):
                trend_headlines.append(item["title"])

    # キーワードがなければデフォルト
    if not trend_keywords:
        trend_keywords = [genre or "テクノロジー"]

    # テンプレートパターンをランダム選択
    templates = [
        _template_list_post,
        _template_opinion_post,
        _template_tips_post,
        _template_question_post,
    ]

    generator = random.choice(templates)
    return generator(trend_keywords, trend_headlines, genre, platform)


def _template_list_post(keywords: list, headlines: list, genre: Optional[str], platform: str) -> str:
    kw = keywords[0] if keywords else "テクノロジー"
    return (
        f"🔥 今話題の「{kw}」まとめ！\n\n"
        f"注目ポイント👇\n"
        f"1. 検索トレンドで急上昇中\n"
        f"2. SNSでも多くの反応\n"
        f"3. 今後さらに注目される可能性大\n\n"
        f"知っておかないとヤバいかも...！\n\n"
        f"#{kw.replace(' ', '')} #トレンド #2026"
    )


def _template_opinion_post(keywords: list, headlines: list, genre: Optional[str], platform: str) -> str:
    kw = keywords[0] if keywords else "テクノロジー"
    headline = headlines[0] if headlines else f"{kw}の最新動向"
    return (
        f"💡 「{headline[:40]}」\n\n"
        f"これ、めちゃくちゃ大事なニュースなのに\n"
        f"まだ知らない人が多すぎる。\n\n"
        f"今のうちにチェックしておくべき。\n"
        f"早く動いた人が勝つ時代。\n\n"
        f"#{kw.replace(' ', '')} #最新ニュース"
    )


def _template_tips_post(keywords: list, headlines: list, genre: Optional[str], platform: str) -> str:
    kw = keywords[0] if keywords else "テクノロジー"
    return (
        f"📌 {kw}について、知っておくべき3つのこと\n\n"
        f"① トレンドが急速に変化している\n"
        f"② 早期参入者が圧倒的に有利\n"
        f"③ 情報収集のスピードが差を生む\n\n"
        f"「まだ早い」と思った時がチャンス。\n\n"
        f"#{kw.replace(' ', '')} #情報発信 #行動力"
    )


def _template_question_post(keywords: list, headlines: list, genre: Optional[str], platform: str) -> str:
    kw = keywords[0] if keywords else "テクノロジー"
    return (
        f"🤔 ぶっちゃけ「{kw}」ってどう思う？\n\n"
        f"最近めちゃくちゃ話題になってるけど、\n"
        f"実際に使ってみた人の感想が聞きたい。\n\n"
        f"良かった点・微妙だった点、\n"
        f"リプで教えてくれたら嬉しい🙏\n\n"
        f"#{kw.replace(' ', '')} #みんなの意見"
    )
