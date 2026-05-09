'''API'''

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import os
import models
import schemas
import time
from dotenv import load_dotenv
from database import engine, SessionLocal
from tasks import updateClickCount
from utils import (get_cache, set_cache, create_url_db, 
                   generate_timestamp_code, check_short_url_exists)
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
models.Base.metadata.create_all(bind=engine)

# @app.get("/health")
# def health_check():
#     print("hola")
#     return {"status":200}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten", response_model=schemas.URLResponse, status_code=201)
@limiter.limit("5/minute")
def create_short_url(request: Request, url_request: schemas.URLRequest, db: Session = Depends(get_db)):
    url_request.url = str(url_request.url)

    existing_url = db.query(models.URL).filter(models.URL.original_url == url_request.url).first()
    if existing_url:
        return schemas.URLResponse(short_url=f"{BASE_URL}/{existing_url.short_code}")
    
    if url_request.custom_alias:
        if not check_short_url_exists(db, url_request.custom_alias):
            short_code = url_request.custom_alias
        else:
            raise HTTPException(status_code=400, detail="Custom alias already exists")
    else:
        short_code = generate_timestamp_code()

    create_url_db(db, url_request.url, short_code)

    return schemas.URLResponse(short_url=f"{BASE_URL}/{short_code}")

@app.get("/{short_code}")
@limiter.limit("10/minute")
def redirect(request: Request, short_code: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    original_url = get_cache(short_code)
    print(f"Cache hit for {short_code}: {original_url}" if original_url else f"Cache miss for {short_code}")
    if not original_url:
        url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
        if not url:
            raise HTTPException(status_code=404, detail="URL not found")
        
        original_url = url.original_url
        set_cache(short_code, original_url)
        print(f"URL found in DB for {short_code}: {original_url}")
    
    background_tasks.add_task(updateClickCount, short_code)

    return RedirectResponse(original_url, status_code=302)
