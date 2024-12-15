from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import URLItem
from database import SessionLocal, engine, Base
from pydantic import BaseModel, HttpUrl
import random
import string
import os

app = FastAPI(
    title="Семинар наставника hw_final shorten_url",
    description="Семинар наставника hw_final shorten_url",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)


class URLCreate(BaseModel):
    url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.example.com"
            }
        }


class URLResponse(BaseModel):
    short_url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "short_url": "http://localhost:8000/abc123"
            }
        }


class URLStats(BaseModel):
    short_id: str
    full_url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "short_id": "abc123",
                "full_url": "https://www.example.com"
            }
        }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.post("/shorten", response_model=URLResponse, status_code=201)
def shorten_url(data: URLCreate, db: Session = Depends(get_db)):
    for _ in range(10):
        short_id = generate_short_id()
        if not db.query(URLItem).filter(URLItem.short_id == short_id).first():
            full_url = str(data.url)
            new_url = URLItem(short_id=short_id, full_url=full_url)
            db.add(new_url)
            db.commit()
            return {"short_url": f"http://localhost:2710/{short_id}"}
    raise HTTPException(status_code=500, detail="Failed to generate a unique short ID.")


@app.get("/{short_id}", response_class=RedirectResponse)
def redirect_to_full(short_id: str, db: Session = Depends(get_db)):
    url_item = db.query(URLItem).filter(URLItem.short_id == short_id).first()
    if url_item:
        return RedirectResponse(url=url_item.full_url)
    raise HTTPException(status_code=404, detail="Short URL not found.")


@app.get("/stats/{short_id}", response_model=URLStats)
def get_stats(short_id: str, db: Session = Depends(get_db)):
    url_item = db.query(URLItem).filter(URLItem.short_id == short_id).first()
    if url_item:
        return {"short_id": short_id, "full_url": url_item.full_url}
    raise HTTPException(status_code=404, detail="Short URL not found.")
