import asyncio
import os
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import async_session
from app.models.user import User
from app.core import hash_password
from sqlalchemy import select

async def create_admin_user():
    email = "admin@autobuzz.com"
    password = "admin_password_1234"  # 初期パスワード
    
    async with async_session() as session:
        # 既存チェック
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User {email} already exists.")
            return

        # 管理者ユーザー作成
        admin_user = User(
            email=email,
            password_hash=hash_password(password),
            is_admin=True,      # 管理者フラグ
            plan_type="pro",    # 最上級プラン
            auto_post_enabled=True
        )
        session.add(admin_user)
        await session.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_admin_user())
