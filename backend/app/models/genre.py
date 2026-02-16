import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import List


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    genre_name: Mapped[str] = mapped_column(String, nullable=False)
    keywords: Mapped[str] = mapped_column(JSON, default="[]")

    user = relationship("User", back_populates="genres")

    @property
    def keywords_list(self) -> List[str]:
        if isinstance(self.keywords, list):
            return self.keywords
        import json
        return json.loads(self.keywords) if self.keywords else []
