import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
