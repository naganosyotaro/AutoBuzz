import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import auth, sns, genres, posts, schedules, affiliate, links, analytics
from app.api import autopilot

logger = logging.getLogger(__name__)

# バックグラウンドスケジューラー
_scheduler_task = None


async def _scheduler_loop():
    """1分ごとにスケジュールチェックして自動投稿を実行"""
    from app.services.auto_scheduler import check_and_run_scheduled

    while True:
        try:
            await check_and_run_scheduled()
        except Exception as e:
            logger.error(f"スケジューラーエラー: {e}")
        await asyncio.sleep(60)  # 1分間待機


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時にDBテーブルを作成
    await init_db()
    # バックグラウンドスケジューラー起動
    global _scheduler_task
    _scheduler_task = asyncio.create_task(_scheduler_loop())
    logger.info("自動投稿スケジューラーを起動しました")
    yield
    # シャットダウン時にスケジューラーを停止
    if _scheduler_task:
        _scheduler_task.cancel()


app = FastAPI(
    title="AutoBuzz API",
    description="SNS自動投稿＆アフィリエイト収益化SaaS",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(sns.router)
app.include_router(genres.router)
app.include_router(posts.router)
app.include_router(schedules.router)
app.include_router(affiliate.router)
app.include_router(links.router)
app.include_router(analytics.router)
app.include_router(autopilot.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AutoBuzz API"}
