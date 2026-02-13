import uuid
import json
import logging
from typing import List
from google.cloud import storage, pubsub_v1

logger = logging.getLogger("enrich-pro-service")
logger.setLevel(logging.INFO)

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()


def log(message: str, **kwargs):
    logger.info(json.dumps({"message": message, **kwargs}))


def generate_id() -> str:
    return str(uuid.uuid4())


def download_from_gcs(bucket: str, file_name: str, local_path: str):
    bucket_obj = storage_client.bucket(bucket)
    blob = bucket_obj.blob(file_name)
    blob.download_to_filename(local_path)
    log("Downloaded from GCS", bucket=bucket, file=file_name)


def download_frames(bucket: str, frame_paths: List[str], local_dir: str) -> List[str]:
    import os
    os.makedirs(local_dir, exist_ok=True)
    local_paths = []
    for frame in frame_paths:
        local_path = os.path.join(local_dir, frame.split("/")[-1])
        download_from_gcs(bucket, frame, local_path)
        local_paths.append(local_path)
    return local_paths


def publish(topic: str, project: str, message: dict) -> str:
    topic_path = publisher.topic_path(project, topic)
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future.result()

