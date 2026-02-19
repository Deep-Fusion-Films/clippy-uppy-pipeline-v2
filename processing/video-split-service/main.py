import os
import json
import base64
from flask import Flask, request

from google.cloud import pubsub_v1
from ffmpeg_splitter import needs_splitting, split_video
from segment_manifest import write_manifest

# -------------------------------
# Cloud Run health server
# -------------------------------
app = Flask(__name__)

@app.get("/")
def health():
    return "ok", 200

# -------------------------------
# Environment + Pub/Sub setup
# -------------------------------
PROJECT_ID = os.environ.get("PROJECT_ID", "deepfusion-clippyuppy-pipeline")
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


# -------------------------------
# Pub/Sub Push Handler (FIXED)
# -------------------------------
@app.post("/")
def pubsub_handler():
    envelope = request.get_json()

    if not envelope or "message" not in envelope:
        return ("Bad Request: no Pub/Sub message received", 400)

    message = envelope["message"]

    # Decode Pub/Sub data
    data = base64.b64decode(message["data"]).decode("utf-8")
    event = json.loads(data)

    # Log for debugging
    print(f"[EVENT] Received: {event}")

    # Call the existing processing logic
    process_event(event)

    return ("", 204)


# -------------------------------
# Existing processing logic
# -------------------------------
def process_event(msg):
    asset_id = msg["asset_id"]
    source = msg["source"]
    video_uri = msg["video_uri"]

    print(f"[PROCESS] Video accepted: {video_uri}")

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


# -------------------------------
# Local dev entrypoint
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
