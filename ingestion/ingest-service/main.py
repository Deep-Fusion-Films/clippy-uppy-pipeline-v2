import os
import json
from google.cloud import pubsub_v1
from asset_registry import register_asset
from validator import validate_ingest_message

PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]  # e.g. "video-split"
publisher = pubsub_v1.PublisherClient()


def publish_next_stage(asset_id: str, source: str, video_uri: str):
    message = {
        "asset_id": asset_id,
        "source": source,
        "video_uri": video_uri,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC)
    publisher.publish(topic_path, data=data).result()


def main(event, context):
    message_data = json.loads(event["data"].decode("utf-8"))

    validate_ingest_message(message_data)

    asset_id = message_data["asset_id"]
    source = message_data["source"]
    video_uri = message_data["video_uri"]

    register_asset(asset_id, source, video_uri)

    publish_next_stage(asset_id, source, video_uri)

