import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SnsAccount(Base):
    __tablename__ = "sns_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    # OAuth 1.0a (X/Twitter)
    access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    access_token_secret: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # OAuth 2.0 (Threads)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # アカウント表示名
    account_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user = relationship("User", back_populates="sns_accounts")
