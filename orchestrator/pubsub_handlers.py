from utils import decode_pubsub_request, log
from pipeline_flash import start_flash_pipeline


def handle_pipeline_start(payload: dict) -> dict:
    """
    Handles Pub/Sub push from ingest-service (pipeline.v2.start).
    """
    unified_asset = decode_pubsub_request(payload)
    if not unified_asset:
        log("Empty or invalid Pub/Sub message")
        return {"status": "ignored"}

    log("Received pipeline start message", asset_id=unified_asset.get("asset_id"))

    message_id = start_flash_pipeline(unified_asset)

    return {
        "status": "ok",
        "asset_id": unified_asset.get("asset_id"),
        "message_id": message_id,
    }

