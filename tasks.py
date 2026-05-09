'''add tasks'''
import models
from database import SessionLocal
from sqlalchemy import select

from datetime import datetime, timezone

def updateClickCount(short_code: str):
    with SessionLocal() as db:
        url_id = db.scalar(
            select(models.URL.id).where(models.URL.short_code == short_code)
        )
        
        if not url_id:
            print(f"[Background Task] Error: URL not found for {short_code}")
            return

        click_record = db.scalar(
            select(models.Click).where(models.Click.url_id == url_id)
        )

        if click_record:
            click_record.timestamp = datetime.now(timezone.utc)
            click_record.count += 1
            print(f"[Background Task] Updated timestamp for URL ID: {url_id}")
        else:
            new_click = models.Click(url_id=url_id)
            db.add(new_click)
            print(f"[Background Task] Created new click record for URL ID: {url_id}")

        db.commit()
