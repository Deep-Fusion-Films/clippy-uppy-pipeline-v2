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
from gemini_audio import transcribe_audio

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
NEXT_TOPIC = os.getenv("FRAME_SAMPLE_TOPIC", "pipeline.v2.frame.sample")

TRANSCRIPT_SUFFIX = "_transcript.txt"

app = FastAPI(title="Audio Transcribe Service", version="1.0.0")


class PipelineMessage(BaseModel):
    asset_id: str
    bucket: str
    file_name: str
    audio_file_name: str
    source: str
    correlation_id: str
    trace_id: str
    metadata: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/transcribe-audio")
async def transcribe_audio_endpoint(request: Request):
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
    local_audio = f"/tmp/{generate_id()}.wav"
    local_transcript = f"/tmp/{generate_id()}.txt"

    # Download audio
    download_from_gcs(payload.bucket, payload.audio_file_name, local_audio)

    # Transcribe
    transcript = transcribe_audio(local_audio)

    # Save transcript locally
    with open(local_transcript, "w") as f:
        f.write(transcript)

    # Upload transcript
    transcript_file_name = payload.file_name + TRANSCRIPT_SUFFIX
    upload_to_gcs(payload.bucket, transcript_file_name, local_transcript)

    # Publish next pipeline event
    next_message = payload.model_dump()
    next_message["transcript_file_name"] = transcript_file_name

    message_id = publish(NEXT_TOPIC, PROJECT_ID, next_message)

    log("Published next pipeline event", message_id=message_id)

    return {
        "status": "ok",
        "asset_id": payload.asset_id,
        "transcript_file": transcript_file_name,
        "message_id": message_id
    }

