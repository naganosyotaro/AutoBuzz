import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    plan_type: Mapped[str] = mapped_column(String, default="free")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_post_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    sns_accounts = relationship("SnsAccount", back_populates="user", cascade="all, delete-orphan")
    genres = relationship("Genre", back_populates="user", cascade="all, delete-orphan")
    generated_posts = relationship("GeneratedPost", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    affiliate_accounts = relationship("AffiliateAccount", back_populates="user", cascade="all, delete-orphan")
    affiliate_offers = relationship("AffiliateOffer", back_populates="user", cascade="all, delete-orphan")
    short_links = relationship("ShortLink", back_populates="user", cascade="all, delete-orphan")
    affiliate_revenues = relationship("AffiliateRevenue", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
