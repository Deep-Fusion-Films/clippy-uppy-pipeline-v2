import os
from utils import publish, log

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
AUDIO_EXTRACT_TOPIC = os.getenv("AUDIO_EXTRACT_TOPIC", "pipeline.v2.audio.extract")


def start_flash_pipeline(unified_asset: dict) -> str:
    """
    Entry point for the real-time Flash pipeline.
    Takes the unified ingest message and sends it to the audio-extract-service topic.
    """
    log("Starting Flash pipeline", asset_id=unified_asset.get("asset_id"))
    message_id = publish(AUDIO_EXTRACT_TOPIC, PROJECT_ID, unified_asset)
    log("Published to audio-extract topic", message_id=message_id)
    return message_id

