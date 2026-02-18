import time
from typing import List
from google.cloud import firestore


db = firestore.Client()


def chunk_list(items: List[dict], size: int) -> List[List[dict]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def wait_for_window_completion(asset_ids: List[str]):
    """
    Polls Firestore until all assets in the window have status=completed.
    Each downstream service updates Firestore:
    /assets/{asset_id} → { "status": "completed" }
    """

    while True:
        completed = 0
        for asset_id in asset_ids:
            doc = db.collection("assets").document(asset_id).get()
            if doc.exists and doc.to_dict().get("status") == "completed":
                completed += 1

        if completed == len(asset_ids):
            return

        time.sleep(1)
