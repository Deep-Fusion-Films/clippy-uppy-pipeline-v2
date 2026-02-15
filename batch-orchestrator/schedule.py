from utils import log
from pipeline_batch import start_batch_pipeline


def run_scheduled_backfill(asset_list: list[dict]):
    """
    Example scheduled job: run batch enrichment on a list of assets.
    """
    results = []
    for asset in asset_list:
        message_id = start_batch_pipeline(asset)
        results.append({"asset_id": asset.get("asset_id"), "message_id": message_id})
    log("Scheduled backfill complete", count=len(results))
    return results

