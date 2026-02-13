import uuid
import json
import logging
from google.cloud import pubsub_v1

logger = logging.getLogger("ingest-service")
logger.setLevel(logging.INFO)

publisher = pubsub_v1.PublisherClient()

def generate_id():
    return str(uuid.uuid4())

def publish(topic: str, project: str, message: dict):
    topic_path = publisher.topic_path(project, topic)
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future.result()

def log(message: str, **kwargs):
    logger.info(json.dumps({"message": message, **kwargs}))

