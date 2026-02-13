import json
from typing import Dict, Any
from google.cloud import storage
from utils import storage_client, log


def store_metadata_gcs(
    bucket_name: str,
    asset_id: str,
    payload: Dict[str, Any],
    prefix: str = "metadata",
):
    bucket = storage_client.bucket(bucket_name)
    blob_path = f"{prefix}/{asset_id}.json"
    blob = bucket.blob(blob_path)

    blob.upload_from_string(
        json.dumps(payload, indent=2),
        content_type="application/json",
    )

    log("Stored metadata in GCS", bucket=bucket_name, path=blob_path)

    return blob_path

