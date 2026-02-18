import os
import json
from google.cloud import pubsub_v1
from ffmpeg_splitter import needs_splitting, split_video
from segment_manifest import write_manifest

PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]  # e.g. "audio-transcribe"
publisher = pubsub_v1.PublisherClient()


def publish_segment_event(asset_id: str, source: str, segment_uri: str, segment_index: int):
    message = {
        "asset_id": asset_id,
        "source": source,
        "segment_uri": segment_uri,
        "segment_index": segment_index,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC)
    publisher.publish(topic_path, data=data).result()


def main(event, context):
    msg = json.loads(event["data"].decode("utf-8"))

    asset_id = msg["asset_id"]
    source = msg["source"]
    video_uri = msg["video_uri"]

    if not needs_splitting(video_uri):
        # No split needed → treat whole video as segment 0
        publish_segment_event(asset_id, source, video_uri, 0)
        write_manifest(asset_id, [video_uri])
        return

    # Split into segments
    segments = split_video(video_uri)

    # Write manifest for merger
    write_manifest(asset_id, segments)

    # Publish each segment
    for idx, segment_uri in enumerate(segments):
        publish_segment_event(asset_id, source, segment_uri, idx)

