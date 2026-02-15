import os
from utils import publish, log

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
BATCH_TOPIC = os.getenv("BATCH_ENRICH_TOPIC", "pipeline.v2.batch.enrich")


def start_batch_pipeline(unified_asset: dict) -> str:
    """
    Sends the unified asset into the Batch API enrichment path.
    """
    log("Starting Batch pipeline", asset_id=unified_asset.get("asset_id"))
    message_id = publish(BATCH_TOPIC, PROJECT_ID, unified_asset)
    log("Published to batch-enrich topic", message_id=message_id)
    return message_id

