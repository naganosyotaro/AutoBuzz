from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas import AutopilotStatus, AutopilotToggle
from app.services.auto_scheduler import run_autopilot_for_user

router = APIRouter(prefix="/api/autopilot", tags=["全自動モード"])


@router.get("/status", response_model=AutopilotStatus)
async def get_autopilot_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """全自動モードの設定状態を取得"""
    return AutopilotStatus(
        enabled=user.auto_post_enabled,
        user_id=user.id,
    )


@router.post("/toggle", response_model=AutopilotStatus)
async def toggle_autopilot(
    body: AutopilotToggle,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """全自動モードのON/OFF切替"""
    user.auto_post_enabled = body.enabled
    await db.flush()
    await db.refresh(user)
    return AutopilotStatus(
        enabled=user.auto_post_enabled,
        user_id=user.id,
    )


@router.post("/run-now")
async def run_autopilot_now(
    user: User = Depends(get_current_user),
):
    """全自動投稿を即時実行（テスト用）"""
    results = await run_autopilot_for_user(user.id)
    return {
        "message": f"{len(results)}件の投稿を生成しました",
        "results": results,
    }
