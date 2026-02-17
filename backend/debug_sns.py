import asyncio
import os
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import async_session
from app.models.user import User
from app.models.sns_account import SnsAccount
from sqlalchemy import select
from app.services.sns_poster import post_to_x

async def debug_sns():
    print("=== SNS Debug Start ===")
    
    # 1. 環境変数の確認 (値そのものは表示せず、設定有無だけ確認)
    print(f"X_API_KEY: {'[SET]' if settings.X_API_KEY else '[MISSING]'}")
    print(f"X_API_SECRET: {'[SET]' if settings.X_API_SECRET else '[MISSING]'}")
    
    # 2. ユーザーとSNSアカウントの確認
    async with async_session() as session:
        # 管理者ユーザー（または最初のユーザー）を取得
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("Error: User not found in DB.")
            return

        print(f"User found: {user.email}")
        
        # SNSアカウント取得
        sns_result = await session.execute(select(SnsAccount).where(SnsAccount.user_id == user.id, SnsAccount.platform == 'x'))
        sns_account = sns_result.scalar_one_or_none()
        
        if not sns_account:
            print("SnsAccount (X) not found in DB.")
            if settings.X_ACCESS_TOKEN:
                print("Falling back to .env X_ACCESS_TOKEN...")
                access_token = settings.X_ACCESS_TOKEN
                access_token_secret = settings.X_ACCESS_TOKEN_SECRET
            else:
                print("Error: No X access token found in DB or .env")
                return
        else:
            print("SnsAccount (X) found in DB.")
            access_token = sns_account.access_token
            access_token_secret = sns_account.access_token_secret

        # 3. 投稿テスト
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

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_sns())
