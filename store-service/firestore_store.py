from typing import Dict, Any
from google.cloud import firestore
from utils import firestore_client, log


def store_metadata_firestore(
    asset_id: str,
    source: str,
    enriched_metadata: Dict[str, Any] | None,
    enriched_metadata_pro: Dict[str, Any] | None,
):
    doc_ref = firestore_client.collection("assets").document(asset_id)

    update_data: Dict[str, Any] = {
        "source": source,
    }

    if enriched_metadata is not None:
        update_data["enriched_flash"] = enriched_metadata

    if enriched_metadata_pro is not None:
        update_data["enriched_pro"] = enriched_metadata_pro

    doc_ref.set(update_data, merge=True)

    log(
        "Stored metadata in Firestore",
        asset_id=asset_id,
        has_flash=enriched_metadata is not None,
        has_pro=enriched_metadata_pro is not None,
    )

