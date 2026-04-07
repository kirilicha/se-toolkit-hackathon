from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    item_type: Literal["book", "movie"]
    title: str = Field(min_length=1, max_length=255)
    rating: int = Field(ge=1, le=10)
    entry_date: date | None = None
    comment: str = Field(default="", max_length=5000)
    is_favorite: bool = False


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatsRead(BaseModel):
    total_items: int
    books_count: int
    movies_count: int
    favorites_count: int
    average_rating: float
