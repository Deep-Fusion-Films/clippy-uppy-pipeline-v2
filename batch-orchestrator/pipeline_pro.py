import os
from utils import publish, log

PROJECT_ID = os.getenv("GCP_PROJECT", "local-project")
PRO_TOPIC = os.getenv("PRO_ENRICH_TOPIC", "pipeline.v2.enrich.pro")


def start_pro_pipeline(unified_asset: dict) -> str:
    """
    Sends the unified asset into the Pro Vision enrichment path.
    """
    log("Starting Pro Vision pipeline", asset_id=unified_asset.get("asset_id"))
    message_id = publish(PRO_TOPIC, PROJECT_ID, unified_asset)
    log("Published to enrich-pro topic", message_id=message_id)
    return message_id

