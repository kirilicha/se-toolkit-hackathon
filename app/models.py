from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    entry_date: Mapped[Date | None] = mapped_column(Date, nullable=True, index=True)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
