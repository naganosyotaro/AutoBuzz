"""
SNS投稿サービス
X (Twitter): OAuth 1.0a User Context (tweepy) を使用
Threads: Meta Graph API を使用
"""
import logging
from typing import Optional
from app.config import settings
import httpx

logger = logging.getLogger(__name__)


async def post_to_x(
    content: str,
    access_token: str,
    access_token_secret: str = "",
) -> dict:
    """
    X (Twitter) API v2 で投稿する。
    OAuth 1.0a User Context 認証（tweepy使用）。
    consumer_key/secret は .env の X_API_KEY / X_API_SECRET を使用。
    """
    # APIキー未設定チェック
    if not settings.X_API_KEY or not settings.X_API_SECRET:
        logger.warning("X_API_KEY / X_API_SECRET が .env に未設定のためモック投稿")
        return {"mock": True, "status": "posted", "platform": "x",
                "message": "X APIキー未設定のためモック投稿しました"}

    if not access_token:
        logger.warning("access_token 未設定のためモック投稿")
        return {"mock": True, "status": "posted", "platform": "x",
                "message": "access_token 未設定のためモック投稿しました"}

    if not access_token_secret:
        logger.warning("access_token_secret 未設定のためモック投稿")
        return {"mock": True, "status": "posted", "platform": "x",
                "message": "access_token_secret 未設定のためモック投稿しました"}

    try:
        import tweepy

        client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        response = client.create_tweet(text=content)
        tweet_id = response.data["id"]
        logger.info(f"X投稿成功: tweet_id={tweet_id}")

        return {
            "mock": False,
            "status": "posted",
            "platform": "x",
            "tweet_id": tweet_id,
            "url": f"https://x.com/i/status/{tweet_id}",
        }

    except tweepy.TweepyException as e:
        logger.error(f"X投稿APIエラー: {e}")
        raise RuntimeError(f"X投稿失敗: {e}")
    except Exception as e:
        logger.error(f"X投稿エラー: {e}")
        raise RuntimeError(f"X投稿エラー: {e}")


async def post_to_threads(
    content: str,
    access_token: str,
    user_id: str = "me",
) -> dict:
    """Threads APIで投稿する。APIキー未設定時はモック結果を返す。"""
    if not access_token:
        logger.warning("Threads access_token 未設定のためモック投稿")
        return {"mock": True, "status": "posted", "platform": "threads",
                "message": "access_token 未設定のためモック投稿しました"}

    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Create media container
            create_response = await client.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads",
                params={
                    "media_type": "TEXT",
                    "text": content,
                    "access_token": access_token,
                },
            )
            create_response.raise_for_status()
            creation_id = create_response.json().get("id")

            # Step 2: Publish
            publish_response = await client.post(
                f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
                params={
                    "creation_id": creation_id,
                    "access_token": access_token,
                },
            )
            publish_response.raise_for_status()
            result = publish_response.json()
            logger.info(f"Threads投稿成功: {result}")
            return {**result, "mock": False, "status": "posted", "platform": "threads"}

    except httpx.HTTPStatusError as e:
        logger.error(f"Threads API エラー: {e.response.status_code} {e.response.text}")
        raise RuntimeError(f"Threads投稿失敗: {e.response.text}")
    except Exception as e:
        logger.error(f"Threads投稿エラー: {e}")
        raise RuntimeError(f"Threads投稿エラー: {e}")
