from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.generated_post import GeneratedPost
from app.schemas import PostGenerateRequest, PostResponse, TrendsResponse
from app.services.ai_generator import generate_post_content
from app.services.buzz_collector import collect_all_trends

router = APIRouter(prefix="/api/posts", tags=["投稿"])


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    user: User = Depends(get_current_user),
):
    """リアルタイムのトレンドデータを取得"""
    trend_data = await collect_all_trends()
    return TrendsResponse(
        google_trends=trend_data.get("google_trends", []),
        news=trend_data.get("news", []),
        x_buzz=trend_data.get("x_buzz", []),
        top_keywords=trend_data.get("top_keywords", []),
    )


@router.post("/generate", response_model=PostResponse, status_code=201)
async def generate_post(
    body: PostGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. トレンドデータを自動収集
    trend_data = await collect_all_trends(
        keywords=[body.genre] if body.genre else None
    )

    # 2. トレンドを参考にAI投稿を生成
    content = await generate_post_content(
        genre=body.genre,
        platform=body.platform,
        trend_data=trend_data,
    )

    generated = GeneratedPost(user_id=user.id, content=content)
    db.add(generated)

    post = Post(
        user_id=user.id,
        platform=body.platform,
        content=content,
        status="draft",
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post).where(Post.user_id == user.id).order_by(Post.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    await db.delete(post)
