'''API'''

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
import schemas
import utils
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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

    short_code = utils.generate_unique_code()

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

    url = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url.original_url, status_code=301)