from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.sns_account import SnsAccount
from app.schemas import SnsAccountCreate, SnsAccountResponse

router = APIRouter(prefix="/api/sns", tags=["SNSアカウント"])


@router.post("/connect/{platform}", response_model=SnsAccountResponse, status_code=201)
async def connect_sns(
    platform: str,
    body: SnsAccountCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if platform not in ("x", "threads"):
        raise HTTPException(status_code=400, detail="対応していないプラットフォームです")

    account = SnsAccount(
        user_id=user.id,
        platform=platform,
        access_token=body.access_token,
        access_token_secret=body.access_token_secret,
        refresh_token=body.refresh_token,
        account_name=body.account_name,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


@router.get("/accounts", response_model=List[SnsAccountResponse])
async def list_accounts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SnsAccount).where(SnsAccount.user_id == user.id)
    )
    return result.scalars().all()


@router.delete("/accounts/{account_id}", status_code=204)
async def delete_account(
    account_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SnsAccount).where(
            SnsAccount.id == account_id,
            SnsAccount.user_id == user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="アカウントが見つかりません")
    await db.delete(account)
