from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os
from utils import (
    log,
    download_from_gcs,
    upload_to_gcs,
    publish,
    generate_id
)
from ffmpeg_extract import extract_audio

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
NEXT_TOPIC = os.getenv("AUDIO_TRANSCRIBE_TOPIC", "pipeline.v2.audio.transcribe")

AUDIO_SUFFIX = "_audio.wav"

app = FastAPI(title="Audio Extract Service", version="1.0.0")


class PipelineMessage(BaseModel):
    asset_id: str
    bucket: str
    file_name: str
    source: str
    correlation_id: str
    trace_id: str
    metadata: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/extract-audio")
async def extract_audio_endpoint(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Pub/Sub wraps messages in {"message": {"data": "..."}}
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
    local_audio = f"/tmp/{generate_id()}.wav"

    # Download video
    download_from_gcs(payload.bucket, payload.file_name, local_video)

    # Extract audio
    extract_audio(local_video, local_audio)

    # Upload audio
    audio_file_name = payload.file_name + AUDIO_SUFFIX
    upload_to_gcs(payload.bucket, audio_file_name, local_audio)

    # Publish next pipeline event
    next_message = payload.model_dump()
    next_message["audio_file_name"] = audio_file_name

    message_id = publish(NEXT_TOPIC, PROJECT_ID, next_message)

    log("Published next pipeline event", message_id=message_id)

    return {
        "status": "ok",
        "asset_id": payload.asset_id,
        "audio_file": audio_file_name,
        "message_id": message_id
    }

