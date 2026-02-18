import os
import json
from google.cloud import pubsub_v1, firestore
from gemini_video import enrich_segment

PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]  # e.g. "segment-merge"
publisher = pubsub_v1.PublisherClient()
db = firestore.Client()


def publish_next_stage(asset_id: str, source: str, segment_index: int):
    message = {
        "asset_id": asset_id,
        "source": source,
        "segment_index": segment_index,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC)
    publisher.publish(topic_path, data=data).result()


def main(event, context):
    msg = json.loads(event["data"].decode("utf-8"))

    asset_id = msg["asset_id"]
    source = msg["source"]
    segment_uri = msg["segment_uri"]
    segment_index = msg["segment_index"]

    metadata = enrich_segment(segment_uri)

    # Store metadata for this segment
    db.collection("vision").document(asset_id).set(
        {str(segment_index): metadata},
        merge=True,
    )

    publish_next_stage(asset_id, source, segment_index)

