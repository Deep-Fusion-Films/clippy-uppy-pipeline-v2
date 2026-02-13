from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List
import os
import shutil
from utils import (
    log,
    download_from_gcs,
    download_frames,
    publish,
    generate_id,
)
from gemini_pro_vision import call_gemini_pro_vision

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
NEXT_TOPIC = os.getenv("STORE_TOPIC_PRO", "pipeline.v2.store.pro")

app = FastAPI(title="Enrich Pro Service (Pro Vision)", version="1.0.0")


class PipelineMessage(BaseModel):
    asset_id: str
    bucket: str
    file_name: str
    transcript_file_name: str
    frames: List[str]
    source: str
    correlation_id: str
    trace_id: str
    metadata: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/enrich-pro")
async def enrich_pro_endpoint(request: Request):
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

    log("Received pipeline message (Pro Vision)", asset_id=payload.asset_id)

    # Local temp paths
    local_transcript = f"/tmp/{generate_id()}.txt"
    frames_dir = f"/tmp/frames_{generate_id()}"

    # Download transcript
    download_from_gcs(payload.bucket, payload.transcript_file_name, local_transcript)

    with open(local_transcript, "r") as f:
        transcript = f.read()

    # Download frames
    local_frames = download_frames(payload.bucket, payload.frames, frames_dir)

    # Call Gemini Pro Vision
    clip_metadata = call_gemini_pro_vision(transcript, local_frames)

    # Cleanup
    shutil.rmtree(frames_dir, ignore_errors=True)

    # Publish to next stage (store-service, pro branch)
    next_message = payload.model_dump()
    next_message["enriched_metadata_pro"] = clip_metadata.model_dump()

    message_id = publish(NEXT_TOPIC, PROJECT_ID, next_message)

    log("Published enriched metadata (Pro Vision)", message_id=message_id)

    return {
        "status": "ok",
        "asset_id": payload.asset_id,
        "message_id": message_id,
    }

