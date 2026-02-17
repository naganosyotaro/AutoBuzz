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

@app.get("/api/setup-admin-user")
async def setup_admin_user():
    """一時的な管理者作成エンドポイント"""
    from app.database import async_session
    from app.models.user import User
    from app.core import hash_password
    from sqlalchemy import select

    email = "admin@autobuzz.com"
    password = "admin_password_1234"
    
    async with async_session() as session:
        # 既存チェック
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return {"message": "Admin user already exists", "email": email}

        # 管理者ユーザー作成
        admin_user = User(
            email=email,
            password_hash=hash_password(password),
            is_admin=True,
            plan_type="pro",
            auto_post_enabled=True
        )
        session.add(admin_user)
        await session.commit()
    
    return {"message": "Admin user created successfully!", "email": email, "password": password}


@app.get("/api/debug-sns")
async def debug_sns_endpoint():
    """SNS設定のデバッグ情報を返すエンドポイント"""
    import io
    import sys
    from contextlib import redirect_stdout
    
    # 標準出力をキャプチャするためのバッファ
    f = io.StringIO()
    
    # 既存のロジックを実行（ただしprint出力したいので、関数化するか、ここで再実装）
    # シンプルにここでロジックを書く
    
    with redirect_stdout(f):
        print("=== SNS Debug Start ===")
        from app.config import settings
        from app.database import async_session
        from app.models.user import User
        from app.models.sns_account import SnsAccount
        from sqlalchemy import select
        from app.services.sns_poster import post_to_x
        import os

        # 1. 環境変数
        print(f"X_API_KEY: {'[SET]' if settings.X_API_KEY else '[MISSING]'}")
        print(f"X_API_SECRET: {'[SET]' if settings.X_API_SECRET else '[MISSING]'}")
        
        async with async_session() as session:
            # 2. ユーザー
            user_result = await session.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            
            if not user:
                print("Error: User not found in DB.")
            else:
                print(f"User found: {user.email}")
                
                # 3. SNSアカウント
                sns_result = await session.execute(select(SnsAccount).where(SnsAccount.user_id == user.id, SnsAccount.platform == 'x'))
                sns_account = sns_result.scalar_one_or_none()
                
                access_token = None
                access_token_secret = None

                if not sns_account:
                    print("SnsAccount (X) not found in DB.")
                    if settings.X_ACCESS_TOKEN:
                        print("Falling back to .env X_ACCESS_TOKEN...")
                        access_token = settings.X_ACCESS_TOKEN
                        access_token_secret = settings.X_ACCESS_TOKEN_SECRET
                    else:
                        print("Error: No X access token found in DB or .env")
                else:
                    print("SnsAccount (X) found in DB.")
                    access_token = sns_account.access_token
                    access_token_secret = sns_account.access_token_secret

                # 4. 投稿テスト
                if access_token:
                    print("Attempting to post test tweet...")
                    try:
                        result = await post_to_x(
                            content=f"AutoBuzz Debug Test {os.urandom(4).hex()}",
                            access_token=access_token,
                            access_token_secret=access_token_secret or ""
                        )
                        print("Result:", result)
                        
                        if result.get("mock"):
                            print("MOOOOOOCK! The post was mocked.")
                            print("Reason:", result.get("message"))
                        else:
                            print("SUCCESS! Posted to X.")
                    except Exception as e:
                        print(f"EXCEPTION during posting: {e}")
                        import traceback
                        traceback.print_exc()

        print("=== SNS Debug End ===")

    output = f.getvalue()
    return {"log": output}



@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AutoBuzz API"}
