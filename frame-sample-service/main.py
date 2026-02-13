from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
import shutil
from utils import (
    log,
    download_from_gcs,
    upload_to_gcs,
    publish,
    generate_id
)
from ffmpeg_sample import extract_frames

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
NEXT_TOPIC = os.getenv("ENRICH_TOPIC", "pipeline.v2.enrich")

app = FastAPI(title="Frame Sample Service", version="1.0.0")


class PipelineMessage(BaseModel):
    asset_id: str
    bucket: str
    file_name: str
    transcript_file_name: str
    source: str
    correlation_id: str
    trace_id: str
    metadata: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/sample-frames")
async def sample_frames_endpoint(request: Request):
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

    log("Received pipeline message", asset_id=payload.asset_id)

    # Local temp paths
    local_video = f"/tmp/{generate_id()}.mp4"
    frames_dir = f"/tmp/frames_{generate_id()}"

    # Download video
    download_from_gcs(payload.bucket, payload.file_name, local_video)

    # Extract frames
    frames = extract_frames(local_video, frames_dir)

    # Upload frames
    uploaded_frames = []
    for frame in frames:
        local_path = os.path.join(frames_dir, frame)
        gcs_name = f"{payload.asset_id}/frames/{frame}"
        upload_to_gcs(payload.bucket, gcs_name, local_path)
        uploaded_frames.append(gcs_name)

    # Cleanup
    shutil.rmtree(frames_dir, ignore_errors=True)

    # Publish next pipeline event
    next_message = payload.model_dump()
    next_message["frames"] = uploaded_frames

    message_id = publish(NEXT_TOPIC, PROJECT_ID, next_message)

    log("Published next pipeline event", message_id=message_id)

    return {
        "status": "ok",
        "asset_id": payload.asset_id,
        "frames_uploaded": len(uploaded_frames),
        "message_id": message_id
    }

