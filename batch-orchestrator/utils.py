import json
import logging
from google.cloud import pubsub_v1

logger = logging.getLogger("batch-orchestrator")
logger.setLevel(logging.INFO)

publisher = pubsub_v1.PublisherClient()


def log(message: str, **kwargs):
    logger.info(json.dumps({"message": message, **kwargs}))


def publish(topic: str, project: str, message: dict) -> str:
    topic_path = publisher.topic_path(project, topic)
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future.result()


def decode_pubsub_request(payload: dict) -> dict:
    msg = payload.get("message", {})
    data = msg.get("data")
    if not data:
        return {}
    import base64
    decoded = base64.b64decode(data).decode("utf-8")
    return json.loads(decoded)

