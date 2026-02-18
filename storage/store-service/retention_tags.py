from google.cloud import storage


def apply_retention_tag(bucket_name: str, object_name: str):
    """
    Applies a metadata tag so GCS lifecycle rules delete after 30 days.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    blob.metadata = blob.metadata or {}
    blob.metadata["retention"] = "30d"
    blob.patch()
