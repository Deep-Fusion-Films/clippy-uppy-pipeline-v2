import os
import json
import base64
from flask import Flask, request

from google.cloud import pubsub_v1, firestore
from gemini_audio import transcribe_audio

# -------------------------------
# Cloud Run health server
# -------------------------------
app = Flask(__name__)

@app.get("/")
def health():
    return "ok", 200


# -------------------------------
# Environment + Clients
# -------------------------------
PROJECT_ID = os.environ["PROJECT_ID"]
NEXT_TOPIC = os.environ["NEXT_TOPIC"]  # e.g. "enrich-vision"

publisher = pubsub_v1.PublisherClient()
db = firestore.Client()


# -------------------------------
# Publish to next stage
# -------------------------------
def publish_next_stage(asset_id: str, source: str, segment_uri: str, segment_index: int):
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
# Pub/Sub Push Handler (Cloud Run)
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

    # Process the event
    process_event(event)

    return ("", 204)


# -------------------------------
# Processing logic
# -------------------------------
def process_event(msg):
    asset_id = msg["asset_id"]
    source = msg["source"]
    segment_uri = msg["segment_uri"]
    segment_index = msg["segment_index"]

    # Transcribe audio
    transcript = transcribe_audio(segment_uri)

    # Store transcript for this segment
    db.collection("transcripts").document(asset_id).set(
        {str(segment_index): transcript},
        merge=True,
    )

    # Publish to next stage
    publish_next_stage(asset_id, source, segment_uri, segment_index)


# -------------------------------
# Local dev entrypoint
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
