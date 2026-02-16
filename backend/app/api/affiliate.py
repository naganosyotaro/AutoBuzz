from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.affiliate_account import AffiliateAccount
from app.models.affiliate_offer import AffiliateOffer
from app.models.affiliate_revenue import AffiliateRevenue
from app.models.short_link import ShortLink
from app.models.click_log import ClickLog
from app.schemas import (
    AffiliateAccountCreate,
    AffiliateAccountResponse,
    AffiliateOfferCreate,
    AffiliateOfferResponse,
    AffiliateStats,
)

router = APIRouter(prefix="/api/affiliate", tags=["アフィリエイト"])


# ─── Accounts ───
@router.post("/accounts", response_model=AffiliateAccountResponse, status_code=201)
async def create_affiliate_account(
    body: AffiliateAccountCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = AffiliateAccount(
        user_id=user.id, platform=body.platform, tracking_id=body.tracking_id
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


@router.get("/accounts", response_model=List[AffiliateAccountResponse])
async def list_affiliate_accounts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AffiliateAccount).where(AffiliateAccount.user_id == user.id)
    )
    return result.scalars().all()


# ─── Offers ───
@router.post("/offers", response_model=AffiliateOfferResponse, status_code=201)
async def create_offer(
    body: AffiliateOfferCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    offer = AffiliateOffer(
        user_id=user.id,
        title=body.title,
        affiliate_url=body.affiliate_url,
        genre=body.genre,
    )
    db.add(offer)
    await db.flush()
    await db.refresh(offer)
    return offer


@router.get("/offers", response_model=List[AffiliateOfferResponse])
async def list_offers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AffiliateOffer).where(AffiliateOffer.user_id == user.id)
    )
    return result.scalars().all()


@router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(
    offer_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AffiliateOffer).where(
            AffiliateOffer.id == offer_id,
            AffiliateOffer.user_id == user.id,
        )
    )
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="案件が見つかりません")
    await db.delete(offer)


# ─── Stats ───
@router.get("/stats", response_model=AffiliateStats)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total clicks
    links_result = await db.execute(
        select(ShortLink.id).where(ShortLink.user_id == user.id)
    )
    link_ids = [row[0] for row in links_result.all()]

    total_clicks = 0
    if link_ids:
        click_result = await db.execute(
            select(func.count()).where(ClickLog.link_id.in_(link_ids))
        )
        total_clicks = click_result.scalar() or 0

    # Total revenue
    rev_result = await db.execute(
        select(func.coalesce(func.sum(AffiliateRevenue.amount), 0.0)).where(
            AffiliateRevenue.user_id == user.id
        )
    )
    total_revenue = float(rev_result.scalar())

    # Offers
    offers_result = await db.execute(
        select(AffiliateOffer).where(AffiliateOffer.user_id == user.id)
    )
    offers = offers_result.scalars().all()

    ctr = 0.0

    return AffiliateStats(
        total_clicks=total_clicks,
        total_revenue=total_revenue,
        ctr=ctr,
        offers=offers,
    )
