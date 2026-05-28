from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime, date, time, timedelta

app = FastAPI()
adverts = {}

class Advertisement(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    price: float
    author: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None

@app.post("/advertisement", response_model=Advertisement)
def create_ad(ad: Advertisement):
    adverts[ad.id] = ad
    return ad

@app.get("/advertisement/{advertisement_id}", response_model=Advertisement)
def get_ad(advertisement_id: UUID = Path(...)):
    ad = adverts.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement)
def update_ad(advertisement_id: UUID, ad_update: AdvertisementUpdate):
    ad = adverts.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    ad_data = ad.dict()
    update_data = ad_update.dict(exclude_unset=True)
    ad_data.update(update_data)
    updated_ad = Advertisement(**ad_data)
    adverts[advertisement_id] = updated_ad
    return updated_ad

@app.delete("/advertisement/{advertisement_id}")
def delete_ad(advertisement_id: UUID):
    if advertisement_id in adverts:
        del adverts[advertisement_id]
        return {"detail": "Deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Advertisement not found")

@app.get("/advertisement", response_model=List[Advertisement])
def search_ads(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    author: Optional[str] = Query(None),
    created_at: Optional[date] = Query(None, description="Фильтр по дате (YYYY-MM-DD)"),
    created_from: Optional[datetime] = Query(None, description="Начало диапазона (ISO datetime)"),
    created_to: Optional[datetime] = Query(None, description="Конец диапазона (ISO datetime)")
):
    results = list(adverts.values())

    if title:
        results = [ad for ad in results if title.lower() in ad.title.lower()]
    if description:
        results = [ad for ad in results if description.lower() in ad.description.lower()]
    if price is not None:
        results = [ad for ad in results if ad.price == price]
    if author:
        results = [ad for ad in results if author.lower() in ad.author.lower()]

    # Фильтрация по created_at (по дню)
    if created_at:
        start = datetime.combine(created_at, time.min)
        end = start + timedelta(days=1)
        results = [ad for ad in results if start <= ad.created_at < end]

    # Фильтрация по диапазону
    if created_from:
        results = [ad for ad in results if ad.created_at >= created_from]
    if created_to:
        results = [ad for ad in results if ad.created_at <= created_to]

    return results