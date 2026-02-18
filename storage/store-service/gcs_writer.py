import json
from google.cloud import storage


def write_metadata_to_gcs(bucket_name: str, object_name: str, metadata: dict) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    blob.upload_from_string(
        json.dumps(metadata, indent=2),
        content_type="application/json"
    )

    return f"gs://{bucket_name}/{object_name}"
