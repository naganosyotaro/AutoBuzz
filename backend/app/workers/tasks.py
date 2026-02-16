from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.collect_buzz_task")
def collect_buzz_task():
    """バズ投稿を定期的に収集するタスク"""
    import asyncio
    from app.services.buzz_collector import collect_buzz_from_x

    async def _run():
        posts = await collect_buzz_from_x(["トレンド", "話題", "バズ"])
        return len(posts)

    result = asyncio.run(_run())
    return {"collected": result}


@celery_app.task(name="app.workers.tasks.auto_post_task")
def auto_post_task():
    """スケジュールに基づいて自動投稿を実行するタスク"""
    import asyncio
    from datetime import datetime, timezone, timedelta

    async def _run():
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        from app.config import settings
        from app.models.schedule import Schedule
        from app.models.sns_account import SnsAccount
        from app.models.post import Post
        from app.services.ai_generator import generate_post_content
        from app.services.sns_poster import post_to_x, post_to_threads

        engine = create_async_engine(settings.DATABASE_URL)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        jst = timezone(timedelta(hours=9))
        now = datetime.now(jst)
        current_time = now.time().replace(second=0, microsecond=0)

        async with session_factory() as db:
            result = await db.execute(
                select(Schedule).where(Schedule.time == current_time)
            )
            schedules = result.scalars().all()

            posted = 0
            for schedule in schedules:
                # Fetch user's SNS accounts
                accounts_result = await db.execute(
                    select(SnsAccount).where(SnsAccount.user_id == schedule.user_id)
                )
                accounts = accounts_result.scalars().all()

                for account in accounts:
                    content = await generate_post_content(platform=account.platform)

                    if account.platform == "x":
                        await post_to_x(content, account.access_token)
                    elif account.platform == "threads":
                        await post_to_threads(content, account.access_token)

                    post = Post(
                        user_id=schedule.user_id,
                        platform=account.platform,
                        content=content,
                        status="posted",
                        posted_at=now,
                    )
                    db.add(post)
                    posted += 1

                await db.commit()

        await engine.dispose()
        return posted

    result = asyncio.run(_run())
    return {"posted": result}
