from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
import os
from utils import log
from firestore_store import store_metadata_firestore
from gcs_store import store_metadata_gcs

METADATA_BUCKET = os.getenv("METADATA_BUCKET", "")

app = FastAPI(title="Store Service", version="1.0.0")


class PipelineMessage(BaseModel):
    asset_id: str
    bucket: str
    file_name: str
    transcript_file_name: Optional[str] = None
    frames: Optional[List[str]] = None
    source: str
    correlation_id: str
    trace_id: str
    metadata: Dict[str, Any]
    enriched_metadata: Optional[Dict[str, Any]] = None
    enriched_metadata_pro: Optional[Dict[str, Any]] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/store")
async def store_endpoint(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Pub/Sub wrapper
    message = payload.get("message", {}).get("data")
    if message:
        import base64
        decoded = base64.b64decode(message).decode("utf-8")
        payload = PipelineMessage.model_validate_json(decoded)
    else:
        payload = PipelineMessage(**payload)

    log(
        "Received store request",
        asset_id=payload.asset_id,
        has_flash=payload.enriched_metadata is not None,
        has_pro=payload.enriched_metadata_pro is not None,
    )

    # Firestore
    store_metadata_firestore(
        asset_id=payload.asset_id,
        source=payload.source,
        enriched_metadata=payload.enriched_metadata,
        enriched_metadata_pro=payload.enriched_metadata_pro,
    )

    # GCS (optional but recommended)
    gcs_path = None
    if METADATA_BUCKET:
        gcs_path = store_metadata_gcs(
            bucket_name=METADATA_BUCKET,
            asset_id=payload.asset_id,
            payload=payload.model_dump(),
        )

    return {
        "status": "ok",
        "asset_id": payload.asset_id,
        "gcs_path": gcs_path,
    }

