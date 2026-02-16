import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AffiliateAccount(Base):
    __tablename__ = "affiliate_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    tracking_id: Mapped[str] = mapped_column(String, nullable=False)

    user = relationship("User", back_populates="affiliate_accounts")
