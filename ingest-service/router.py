from fastapi import APIRouter, Request, HTTPException
from handlers.newsflare_handler import handle_newsflare_gcs_event

router = APIRouter()

@router.post("/ingest/gcs")
async def ingest_gcs(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    try:
        result = handle_newsflare_gcs_event(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

