import os
import json
import uuid
from flask import Flask, request
from google.cloud import pubsub_v1

app = Flask(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
PUBSUB_TOPIC = os.environ["INGEST_TOPIC"]


# -----------------------------
# Helpers
# -----------------------------

def is_video_file(name: str) -> bool:
    """Return True if the object name ends with a supported video extension."""
    return name.lower().endswith((
        ".mp4", ".mov", ".mkv", ".avi", ".mxf"
    ))


def is_direct_upload(name: str) -> bool:
    """Return True if the object is inside the direct-upload/ folder."""
    return name.startswith("direct-upload/")


def publish_event(asset_id: str, gcs_uri: str):
    """Publish the ingestion event to Pub/Sub."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

    message = {
        "asset_id": asset_id,
        "source": "uploads",
        "video_uri": gcs_uri,
    }

    publisher.publish(topic_path, json.dumps(message).encode("utf-8")).result()
    print(f"[PUBSUB] Published event: {message}")


# -----------------------------
# Cloud Run HTTP entrypoint
# -----------------------------

@app.post("/")
def handle_event():
    """
    Entry point for Eventarc → Cloud Run.
    Expects a CloudEvent-style JSON envelope.
    """
    envelope = request.get_json(silent=True)

    if not envelope:
        print("[ERROR] No JSON payload")
        return "bad-request", 400

    event_data = envelope.get("data", {})
    if not event_data:
        print("[ERROR] Missing 'data' field in CloudEvent")
        return "bad-request", 400

    bucket = event_data.get("bucket")
    name = event_data.get("name")

    if not bucket or not name:
        print("[ERROR] Missing bucket or object name")
        return "bad-request", 400

    print(f"[EVENT] Received: gs://{bucket}/{name}")

    # -----------------------------
    # Folder filtering
    # -----------------------------
    if not is_direct_upload(name):
        print(f"[SKIP] Ignoring non-direct-upload file: {name}")
        return "ignored", 200

    # -----------------------------
    # File type filtering
    # -----------------------------
    if not is_video_file(name):
        print(f"[SKIP] Ignoring non-video file: {name}")
        return "ignored", 200

    # -----------------------------
    # Generate asset ID
    # -----------------------------
    asset_id = str(uuid.uuid4())
    gcs_uri = f"gs://{bucket}/{name}"

    print(f"[PROCESS] Video accepted: {gcs_uri}")
    print(f"[PROCESS] Generated asset_id: {asset_id}")

    # -----------------------------
    # Publish to Pub/Sub
    # -----------------------------
    publish_event(asset_id, gcs_uri)

    return "ok", 200


# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def health():
    return "ok", 200


# -----------------------------
# Cloud Run startup
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
