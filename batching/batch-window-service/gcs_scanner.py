from google.cloud import storage
import uuid


def list_videos_in_folder(folder_uri: str):
    """
    Returns a list of:
    {
        "asset_id": "...",
        "gcs_uri": "gs://bucket/path/file.mp4"
    }
    """

    assert folder_uri.startswith("gs://")
    parts = folder_uri.replace("gs://", "").split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1]

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)

    videos = []
    for blob in blobs:
        name = blob.name.lower()
        if name.endswith((".mp4", ".mov", ".mkv", ".avi", ".mxf")):
            videos.append(
                {
                    "asset_id": str(uuid.uuid4()),
                    "gcs_uri": f"gs://{bucket_name}/{blob.name}",
                }
            )

    return videos
