import os
import json
import uuid
from google.cloud import pubsub_v1

# -------------------------------
# Cloud Run health server (required)
# -------------------------------
from flask import Flask
import threading

app = Flask(__name__)

@app.get("/")
def health():
    return "ok", 200

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Start health server in background thread
threading.Thread(target=start_health_server, daemon=True).start()
# -------------------------------


PROJECT_ID = os.environ["PROJECT_ID"]
PUBSUB_TOPIC = os.environ["INGEST_TOPIC"]


def publish_event(asset_id: str, gcs_uri: str):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

    message = {
        "asset_id": asset_id,
        "source": "uploads",
        "video_uri": gcs_uri,
    }

    publisher.publish(topic_path, json.dumps(message).encode("utf-8")).result()


def main(event, context):
    bucket = event["bucket"]
    name = event["name"]

    # Only process video files
    if not name.lower().endswith((".mp4", ".mov", ".mkv", ".avi", ".mxf")):
        return

    gcs_uri = f"gs://{bucket}/{name}"
    asset_id = str(uuid.uuid4())

    publish_event(asset_id, gcs_uri)
