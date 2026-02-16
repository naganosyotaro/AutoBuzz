from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.genre import Genre
from app.schemas import GenreCreate, GenreResponse

router = APIRouter(prefix="/api/genres", tags=["ジャンル"])


@router.post("/", response_model=GenreResponse, status_code=201)
async def create_genre(
    body: GenreCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    genre = Genre(user_id=user.id, genre_name=body.genre_name, keywords=body.keywords)
    db.add(genre)
    await db.flush()
    await db.refresh(genre)
    return genre


@router.get("/", response_model=List[GenreResponse])
async def list_genres(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Genre).where(Genre.user_id == user.id))
    return result.scalars().all()


@router.delete("/{genre_id}", status_code=204)
async def delete_genre(
    genre_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Genre).where(Genre.id == genre_id, Genre.user_id == user.id)
    )
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="ジャンルが見つかりません")
    await db.delete(genre)
