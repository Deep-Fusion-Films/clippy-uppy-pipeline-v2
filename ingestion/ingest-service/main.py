import os
import json
import base64
from flask import Flask, request
from google.cloud import pubsub_v1

from asset_registry import register_asset
from validator import validate_ingest_message

app = Flask(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]
publisher = pubsub_v1.PublisherClient()

# -------------------------------
# Health check
# -------------------------------
@app.get("/")
def health():
    return "ok", 200

# -------------------------------
# Pub/Sub push handler
# -------------------------------
@app.post("/")
def pubsub_handler():
    envelope = request.get_json()

    if not envelope or "message" not in envelope:
        return ("Bad Request", 400)

    message = envelope["message"]

    # Decode Pub/Sub message
    data = base64.b64decode(message["data"]).decode("utf-8")
    message_data = json.loads(data)

    # Validate and process
    validate_ingest_message(message_data)

    asset_id = message_data["asset_id"]
    source = message_data["source"]
    video_uri = message_data["video_uri"]

    register_asset(asset_id, source, video_uri)
    publish_next_stage(asset_id, source, video_uri)

    return ("", 204)

# -------------------------------
# Publish next stage
# -------------------------------
def publish_next_stage(asset_id: str, source: str, video_uri: str):
    message = {
        "asset_id": asset_id,
        "source": source,
        "video_uri": video_uri,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, NEXT_TOPIC)
    publisher.publish(topic_path, data=data).result()

# -------------------------------
# Start server
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
