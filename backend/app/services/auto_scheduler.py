"""
自動投稿スケジューラーサービス
全自動おまかせモード: ジャンル×プラットフォームでトレンド収集→投稿生成→SNS投稿
"""
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.user import User
from app.models.genre import Genre
from app.models.schedule import Schedule
from app.models.post import Post
from app.models.generated_post import GeneratedPost
from app.models.sns_account import SnsAccount
from app.services.buzz_collector import collect_all_trends
from app.services.ai_generator import generate_post_content
from app.services.sns_poster import post_to_x, post_to_threads

logger = logging.getLogger(__name__)

PLATFORMS = ["x", "threads"]


async def run_autopilot_for_user(user_id: str) -> list:
    """
    指定ユーザーの全ジャンル × 全プラットフォームで
    トレンド収集 → 投稿生成 → SNS投稿を実行する
    """
    results = []

    async with async_session() as db:
        # ユーザー取得
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.auto_post_enabled:
            return results

        # ジャンル取得
        genres_result = await db.execute(select(Genre).where(Genre.user_id == user_id))
        genres = genres_result.scalars().all()

        if not genres:
            # ジャンル未設定の場合はデフォルトで1回実行
            genres = [type("GenreMock", (), {"genre_name": None, "keywords_list": []})()]

        # SNSアカウント取得
        sns_result = await db.execute(select(SnsAccount).where(SnsAccount.user_id == user_id))
        sns_accounts = {a.platform: a for a in sns_result.scalars().all()}

        for genre in genres:
            genre_name = getattr(genre, "genre_name", None)
            keywords = getattr(genre, "keywords_list", []) if hasattr(genre, "keywords_list") else []

            # トレンド収集
            try:
                trend_data = await collect_all_trends(keywords=keywords or None)
            except Exception as e:
                logger.warning(f"トレンド収集失敗 (genre={genre_name}): {e}")
                trend_data = None

            for platform in PLATFORMS:
                try:
                    # AI投稿生成
                    content = await generate_post_content(
                        genre=genre_name,
                        platform=platform,
                        trend_data=trend_data,
                    )

                    # DB保存
                    generated = GeneratedPost(user_id=user_id, content=content)
                    db.add(generated)

                    post = Post(
                        user_id=user_id,
                        platform=platform,
                        content=content,
                        status="pending",
                    )
                    db.add(post)
                    await db.flush()
                    await db.refresh(post)

                    # SNS投稿実行
                    sns_account = sns_accounts.get(platform)
                    posted = False
                    post_error = None

                    if sns_account and sns_account.access_token:
                        try:
                            if platform == "x":
                                result = await post_to_x(
                                    content,
                                    sns_account.access_token,
                                    sns_account.access_token_secret or "",
                                )
                            elif platform == "threads":
                                result = await post_to_threads(
                                    content,
                                    sns_account.access_token,
                                )
                            # モック投稿でないか確認
                            posted = not result.get("mock", False)
                            if result.get("mock"):
                                logger.info(f"モック投稿: {result.get('message', '')}")
                        except Exception as e:
                            post_error = str(e)
                            logger.error(f"SNS投稿失敗 ({platform}): {e}")
                    else:
                        post_error = f"SNSアカウント未連携 ({platform})"
                        logger.warning(post_error)

                    # ステータス更新
                    from datetime import datetime, timezone
                    if posted:
                        post.status = "posted"
                        post.posted_at = datetime.now(timezone.utc)
                    else:
                        post.status = "draft"

                    results.append({
                        "post_id": post.id,
                        "platform": platform,
                        "genre": genre_name,
                        "content": content[:80],
                        "status": post.status,
                    })

                except Exception as e:
                    logger.error(f"自動投稿エラー (genre={genre_name}, platform={platform}): {e}")
                    results.append({
                        "platform": platform,
                        "genre": genre_name,
                        "error": str(e),
                        "status": "error",
                    })

        await db.commit()

    return results


async def check_and_run_scheduled():
    """
    現在時刻がスケジュールに一致する全ユーザーの自動投稿を実行する。
    1分ごとにバックグラウンドスケジューラーから呼ばれる。
    """
    from datetime import datetime, timezone, timedelta

    now_jst = datetime.now(timezone(timedelta(hours=9)))
    current_time = now_jst.strftime("%H:%M")
    current_weekday = now_jst.weekday()  # 0=月, 6=日

    logger.info(f"スケジュールチェック: {current_time} (weekday={current_weekday})")

    async with async_session() as db:
        # auto_post_enabled=True のユーザーのスケジュールを取得
        result = await db.execute(
            select(Schedule, User)
            .join(User, Schedule.user_id == User.id)
            .where(User.auto_post_enabled == True)
        )
        rows = result.all()

        for schedule, user in rows:
            schedule_time = schedule.time
            frequency = schedule.frequency

            # 時刻比較（HH:MM形式）
            if schedule_time != current_time:
                continue

            # 頻度チェック
            if frequency == "weekdays" and current_weekday >= 5:
                continue
            if frequency == "weekends" and current_weekday < 5:
                continue

            # 実行
            logger.info(f"自動投稿実行: user={user.email}, time={schedule_time}")
            try:
                results = await run_autopilot_for_user(user.id)
                logger.info(f"自動投稿結果: {len(results)}件 生成")
            except Exception as e:
                logger.error(f"自動投稿失敗: user={user.email}, error={e}")
