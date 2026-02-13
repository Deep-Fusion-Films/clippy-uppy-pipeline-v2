import uuid
import json
import logging
from google.cloud import storage, pubsub_v1

logger = logging.getLogger("audio-extract-service")
logger.setLevel(logging.INFO)

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()


def log(message: str, **kwargs):
    logger.info(json.dumps({"message": message, **kwargs}))


def generate_id():
    return str(uuid.uuid4())


def download_from_gcs(bucket: str, file_name: str, local_path: str):
    bucket_obj = storage_client.bucket(bucket)
    blob = bucket_obj.blob(file_name)
    blob.download_to_filename(local_path)
    log("Downloaded video", bucket=bucket, file=file_name)


def upload_to_gcs(bucket: str, file_name: str, local_path: str):
    bucket_obj = storage_client.bucket(bucket)
    blob = bucket_obj.blob(file_name)
    blob.upload_from_filename(local_path)
    log("Uploaded audio", bucket=bucket, file=file_name)


def publish(topic: str, project: str, message: dict):
    topic_path = publisher.topic_path(project, topic)
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future.result()

