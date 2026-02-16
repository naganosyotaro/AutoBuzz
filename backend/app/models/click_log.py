import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ClickLog(Base):
    __tablename__ = "click_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    link_id: Mapped[str] = mapped_column(String, ForeignKey("short_links.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    link = relationship("ShortLink", back_populates="click_logs")
