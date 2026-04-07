from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import CollectionItem
from .schemas import ItemCreate, ItemRead, ItemUpdate, StatsRead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Collection", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/items", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = CollectionItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/items", response_model=list[ItemRead])
def list_items(
    sort_by: Literal["created_at", "title", "rating", "entry_date"] = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    item_type: Literal["all", "book", "movie"] = Query(default="all"),
    favorite_only: bool = Query(default=False),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(CollectionItem)

    if item_type != "all":
        query = query.filter(CollectionItem.item_type == item_type)
    if favorite_only:
        query = query.filter(CollectionItem.is_favorite.is_(True))
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(or_(CollectionItem.title.ilike(like), CollectionItem.comment.ilike(like)))

    sort_column = {
        "created_at": CollectionItem.created_at,
        "title": CollectionItem.title,
        "rating": CollectionItem.rating,
        "entry_date": CollectionItem.entry_date,
    }[sort_by]

    ordering = asc(sort_column) if order == "asc" else desc(sort_column)
    items = query.order_by(ordering, desc(CollectionItem.created_at)).all()
    return items


@app.get("/api/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CollectionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/api/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(CollectionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CollectionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None


@app.get("/api/stats", response_model=StatsRead)
def get_stats(db: Session = Depends(get_db)):
    total_items = db.query(func.count(CollectionItem.id)).scalar() or 0
    books_count = db.query(func.count(CollectionItem.id)).filter(CollectionItem.item_type == "book").scalar() or 0
    movies_count = db.query(func.count(CollectionItem.id)).filter(CollectionItem.item_type == "movie").scalar() or 0
    favorites_count = db.query(func.count(CollectionItem.id)).filter(CollectionItem.is_favorite.is_(True)).scalar() or 0
    average_rating = db.query(func.avg(CollectionItem.rating)).scalar() or 0

    return StatsRead(
        total_items=total_items,
        books_count=books_count,
        movies_count=movies_count,
        favorites_count=favorites_count,
        average_rating=round(float(average_rating), 2),
    )
