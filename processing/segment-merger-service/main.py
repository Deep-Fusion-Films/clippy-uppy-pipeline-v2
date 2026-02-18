import os
import json
from google.cloud import pubsub_v1, firestore

from merge_logic import merge_segments
from timeline_builder import build_timeline

PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]  # e.g. "store-metadata"
publisher = pubsub_v1.PublisherClient()
db = firestore.Client()


def publish_next_stage(asset_id: str, source: str):
    message = {
        "asset_id": asset_id,
        "source": source,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC)
    publisher.publish(topic_path, data=data).result()


def main(event, context):
    msg = json.loads(event["data"].decode("utf-8"))

    asset_id = msg["asset_id"]
    source = msg["source"]
    segment_index = msg["segment_index"]

    # Fetch all required data
    manifest = db.collection("manifests").document(asset_id).get().to_dict()
    transcripts = db.collection("transcripts").document(asset_id).get().to_dict()
    vision = db.collection("vision").document(asset_id).get().to_dict()

    if not manifest or not transcripts or not vision:
        # Not all segments have arrived yet
        return

    segments = manifest["segments"]
    total_segments = len(segments)

    # Ensure we have all segment metadata
    if len(transcripts) < total_segments or len(vision) < total_segments:
        return

    # Merge everything
    merged = merge_segments(transcripts, vision)
    timeline = build_timeline(transcripts, vision)

    final_metadata = {
        "asset_id": asset_id,
        "source": source,
        "segments": segments,
        "transcript": merged["transcript"],
        "vision": merged["vision"],
        "timeline": timeline,
    }

    # Store final metadata
    db.collection("final").document(asset_id).set(final_metadata)

    # Mark asset as completed for batch-window-service
    db.collection("assets").document(asset_id).set({"status": "completed"}, merge=True)

    publish_next_stage(asset_id, source)

