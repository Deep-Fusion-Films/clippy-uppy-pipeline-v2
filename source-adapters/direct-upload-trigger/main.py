import os
import json
import uuid
from flask import Flask, request
from google.cloud import pubsub_v1

app = Flask(__name__)

# -----------------------------
# Lazy-loaded environment vars
# -----------------------------

def get_project_id():
    project_id = os.environ.get("PROJECT_ID")
    if not project_id:
        raise RuntimeError("Missing required env var: PROJECT_ID")
    return project_id


def get_pubsub_topic():
    topic = os.environ.get("INGEST_TOPIC")
    if not topic:
        raise RuntimeError("Missing required env var: INGEST_TOPIC")
    return topic


# -----------------------------
# Helpers
# -----------------------------

def is_video_file(name: str) -> bool:
    return name.lower().endswith((".mp4", ".mov", ".mkv", ".avi", ".mxf"))


def is_direct_upload(name: str) -> bool:
    return name.startswith("direct-upload/")


def publish_event(asset_id: str, gcs_uri: str):
    publisher = pubsub_v1.PublisherClient()

    project_id = get_project_id()
    topic_name = get_pubsub_topic()

    topic_path = publisher.topic_path(project_id, topic_name)

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

    if not is_direct_upload(name):
        print(f"[SKIP] Ignoring non-direct-upload file: {name}")
        return "ignored", 200

    if not is_video_file(name):
        print(f"[SKIP] Ignoring non-video file: {name}")
        return "ignored", 200

    asset_id = str(uuid.uuid4())
    gcs_uri = f"gs://{bucket}/{name}"

    print(f"[PROCESS] Video accepted: {gcs_uri}")
    print(f"[PROCESS] Generated asset_id: {asset_id}")

    publish_event(asset_id, gcs_uri)

    return "ok", 200


@app.get("/")
def health():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
