import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Event, Publication, Work, Galleryitem

app = FastAPI(title="Theatre Studio Nepal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Theatre Studio Nepal API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Helper to convert ObjectId in results
class _Doc(BaseModel):
    id: str
    data: dict


def _serialize_docs(docs: List[dict]):
    out = []
    for d in docs:
        d = dict(d)
        if d.get("_id"):
            d["id"] = str(d.pop("_id"))
        out.append(d)
    return out


# Events endpoints
@app.post("/api/events", response_model=dict)
async def create_event(event: Event):
    try:
        _id = create_document("event", event)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events", response_model=List[dict])
async def list_events(status: Optional[str] = None, limit: int = 50):
    try:
        filt = {"status": status} if status else {}
        docs = get_documents("event", filt, limit)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Publications
@app.post("/api/publications", response_model=dict)
async def create_publication(pub: Publication):
    try:
        _id = create_document("publication", pub)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/publications", response_model=List[dict])
async def list_publications(limit: int = 100):
    try:
        docs = get_documents("publication", {}, limit)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Works
@app.post("/api/works", response_model=dict)
async def create_work(work: Work):
    try:
        _id = create_document("work", work)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/works", response_model=List[dict])
async def list_works(limit: int = 100):
    try:
        docs = get_documents("work", {}, limit)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Gallery
@app.post("/api/gallery", response_model=dict)
async def create_gallery_item(item: Galleryitem):
    try:
        _id = create_document("galleryitem", item)
        return {"id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gallery", response_model=List[dict])
async def list_gallery(limit: int = 100):
    try:
        docs = get_documents("galleryitem", {}, limit)
        return _serialize_docs(docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Seeder endpoint to populate sample content
@app.post("/api/seed")
async def seed_sample_content():
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")

        report = {"event": 0, "publication": 0, "work": 0, "galleryitem": 0}

        # Only seed if collections are empty
        if db["event"].count_documents({}) == 0:
            sample_events = [
                {
                    "title": "Rituals of the Valley",
                    "date": "2025-12-05",
                    "status": "live",
                    "venue": "Studio Black Box",
                    "city": "Kathmandu",
                    "description": "An immersive performance exploring memory, migration, and the valley's changing rhythms.",
                    "cover_image": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=1600&auto=format&fit=crop",
                },
                {
                    "title": "Echoes of the Himalaya",
                    "date": "2026-01-12",
                    "status": "upcoming",
                    "venue": "Yala Theatre",
                    "city": "Patan",
                    "description": "A new devised work that weaves folk melodies with contemporary movement.",
                    "cover_image": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?q=80&w=1600&auto=format&fit=crop",
                },
            ]
            for e in sample_events:
                create_document("event", e)
                report["event"] += 1

        if db["publication"].count_documents({}) == 0:
            sample_pubs = [
                {
                    "title": "Notes from the Studio",
                    "authors": ["Theatre Studio Nepal"],
                    "year": 2024,
                    "link": "https://example.org/notes",
                    "summary": "A collection of essays on devising, dramaturgy, and community practice.",
                },
                {
                    "title": "Kathmandu Playwrights Anthology",
                    "authors": ["Various"],
                    "year": 2023,
                    "link": "https://example.org/anthology",
                    "summary": "Original plays developed through our writers' lab.",
                },
            ]
            for p in sample_pubs:
                create_document("publication", p)
                report["publication"] += 1

        if db["work"].count_documents({}) == 0:
            sample_works = [
                {
                    "title": "Dust and Devotion",
                    "type": "production",
                    "year": 2022,
                    "description": "A physical theatre piece inspired by city rituals.",
                    "images": ["https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=1600&auto=format&fit=crop"],
                },
                {
                    "title": "Writing the City",
                    "type": "workshop",
                    "year": 2024,
                    "description": "A dramaturgy workshop for early-career artists.",
                    "images": ["https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=1600&auto=format&fit=crop"],
                },
            ]
            for w in sample_works:
                create_document("work", w)
                report["work"] += 1

        if db["galleryitem"].count_documents({}) == 0:
            sample_gallery = [
                {"title": "Rehearsal Warmup", "image_url": "https://images.unsplash.com/photo-1515165562835-c3b8c19b42b1?q=80&w=1600&auto=format&fit=crop"},
                {"title": "Backstage", "image_url": "https://images.unsplash.com/photo-1552709829-6bf1297bd8ff?q=80&w=1600&auto=format&fit=crop"},
                {"title": "Curtain Call", "image_url": "https://images.unsplash.com/photo-1515169067865-5387ec356754?q=80&w=1600&auto=format&fit=crop"},
            ]
            for g in sample_gallery:
                create_document("galleryitem", g)
                report["galleryitem"] += 1

        return {"seeded": report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
