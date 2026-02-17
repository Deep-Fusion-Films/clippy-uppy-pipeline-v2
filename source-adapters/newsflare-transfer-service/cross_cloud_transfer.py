import tempfile
from typing import Optional

import requests
from google.cloud import storage


def _download_to_tempfile(url: str) -> str:
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()

    fd, path = tempfile.mkstemp(suffix=".mp4")
    with open(fd, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    return path


def transfer_to_gcs(remote_url: str, bucket_name: str, object_name: str) -> str:
    local_path = _download_to_tempfile(remote_url)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_path)

    return f"gs://{bucket_name}/{object_name}"
