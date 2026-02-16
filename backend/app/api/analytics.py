from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.short_link import ShortLink
from app.models.click_log import ClickLog
from app.models.affiliate_revenue import AffiliateRevenue
from app.schemas import DashboardStats, PostResponse

router = APIRouter(prefix="/api/dashboard", tags=["ダッシュボード"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total posts
    post_count_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.user_id == user.id)
    )
    total_posts = post_count_result.scalar() or 0

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

    # CTR
    ctr = 0.0

    # Recent posts
    posts_result = await db.execute(
        select(Post)
        .where(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .limit(10)
    )
    recent_posts = posts_result.scalars().all()

    return DashboardStats(
        total_posts=total_posts,
        total_clicks=total_clicks,
        total_revenue=total_revenue,
        ctr=ctr,
        recent_posts=recent_posts,
    )
