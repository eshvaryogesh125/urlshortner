'''API'''

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
import schemas
import utils
import time
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

CACHE = {}

@app.get("/health")
def health_check():
    print("hola")
    return {"status":200}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten")
def create_short_url(request: schemas.URLRequest, db: Session = Depends(get_db)):

    existing_url = db.query(models.URL).filter(models.URL.original_url == request.url).first()
    if existing_url:
        return {
            "short_url": f"http://localhost:8000/{existing_url.short_code}"
        }

    short_code = utils.generate_timestamp_code()

    new_url = models.URL(
        original_url=request.url,
        short_code=short_code
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "short_url": f"http://localhost:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):

    original_url = get_cache(short_code)
    print(f"Cache hit for {short_code}: {original_url}" if original_url else f"Cache miss for {short_code}")
    if not original_url:
        url = db.query(models.URL).filter(
            models.URL.short_code == short_code
        ).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL not found")
        
        original_url = url.original_url if url else None
        set_cache(short_code, original_url)
        print(f"URL found in DB for {short_code}: {original_url}" if url else f"No URL found in DB for {short_code}")


    return RedirectResponse(original_url, status_code=301)

def get_cache(short_code):
    print(f"Checking cache for {short_code}, Current cache state: {CACHE}")
    if short_code in CACHE:
        original_url, expiry = CACHE[short_code]
        if time.time() > expiry:
            del CACHE[short_code]
            return None
        return original_url
    return None

def set_cache(short_code, original_url, ttl=600):
    expiry = time.time() + ttl
    CACHE[short_code] = (original_url, expiry)