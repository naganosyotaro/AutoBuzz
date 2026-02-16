import string
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.short_link import ShortLink
from app.models.click_log import ClickLog
from app.schemas import ShortLinkCreate, ShortLinkResponse

router = APIRouter(prefix="/api/links", tags=["短縮URL"])


def _generate_code(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post("/", response_model=ShortLinkResponse, status_code=201)
async def create_short_link(
    body: ShortLinkCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    code = _generate_code()
    link = ShortLink(
        user_id=user.id, original_url=body.original_url, short_code=code
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


@router.get("/r/{short_code}")
async def redirect_link(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ShortLink).where(ShortLink.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="リンクが見つかりません")

    click = ClickLog(link_id=link.id)
    db.add(click)
    await db.flush()
    return RedirectResponse(url=link.original_url, status_code=302)
