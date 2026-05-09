'''API'''

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
import schemas
import time
from database import engine, SessionLocal
from tasks import updateClickCount
from utils import *

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
def create_short_url(request: schemas.URLRequest, db: Session = Depends(get_db)):

    existing_url = db.query(models.URL).filter(models.URL.original_url == request.url).first()
    if existing_url:
        return schemas.URLResponse(short_url=f"http://localhost:8000/{existing_url.short_code}")
    
    if request.custom_alias:
        if not check_short_url_exists(db, request.custom_alias):
            short_code = request.custom_alias
        else:
            raise HTTPException(status_code=400, detail="Custom alias already exists")
    else:
        short_code = generate_timestamp_code()

    create_url_db(db, request.url, short_code)

    return schemas.URLResponse(short_url=f"http://localhost:8000/{short_code}")

@app.get("/{short_code}")
def redirect(short_code: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
