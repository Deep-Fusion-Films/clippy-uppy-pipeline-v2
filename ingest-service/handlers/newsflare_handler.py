from models import GcsEvent, UnifiedAsset
from utils import generate_id, publish, log

PROJECT_ID = "deep-fusion-films"  # replace with env var later
TOPIC = "pipeline.v2.start"

def handle_newsflare_gcs_event(payload: dict):
    # Accept both raw and wrapped GCS events
    data = payload.get("data", payload)

    event = GcsEvent(
        bucket=data["bucket"],
        name=data["name"],
        metadata=data.get("metadata"),
        source=data.get("source", "newsflare")
    )

    log("Received ingest event", bucket=event.bucket, name=event.name)

    asset = UnifiedAsset(
        asset_id=generate_id(),
        source=event.source,
        bucket=event.bucket,
        file_name=event.name,
        metadata=event.metadata or {},
        correlation_id=generate_id(),
        trace_id=generate_id(),
    )

    message_id = publish(TOPIC, PROJECT_ID, asset.model_dump())

    log("Published unified asset", asset_id=asset.asset_id, message_id=message_id)

    return {
        "status": "ok",
        "asset_id": asset.asset_id,
        "message_id": message_id,
        "source": asset.source,
    }

