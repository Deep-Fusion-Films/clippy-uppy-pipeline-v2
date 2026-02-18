import os
import json
from typing import List

from google.cloud import pubsub_v1
from getty_api import GettyClient
from downloader import download_to_tempfile, upload_to_gcs

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
GCS_RAW_BUCKET = os.environ["RAW_VIDEO_BUCKET"]
GCS_SOURCE_PREFIX = "getty"  # used to build gs:// paths


def publish_asset_event(publisher: pubsub_v1.PublisherClient, asset_id: str, gcs_uri: str):
    message = {
        "asset_id": asset_id,
        "source": "getty",
        "video_uri": gcs_uri,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
    future = publisher.publish(topic_path, data=data)
    future.result()


def process_new_assets():
    getty = GettyClient(
        api_key=os.environ["GETTY_API_KEY"],
        api_secret=os.environ["GETTY_API_SECRET"],
    )
    publisher = pubsub_v1.PublisherClient()

    assets = getty.list_new_videos()
    for asset in assets:
        asset_id = asset["id"]
        video_url = asset["video_url"]

        local_path = download_to_tempfile(video_url)
        gcs_path = f"{GCS_SOURCE_PREFIX}/{asset_id}.mp4"
        gcs_uri = upload_to_gcs(local_path, GCS_RAW_BUCKET, gcs_path)

        publish_asset_event(publisher, asset_id, gcs_uri)


def main(request=None):
    # HTTP entrypoint (for Cloud Run / Functions style)
    process_new_assets()
    return ("OK", 200)


if __name__ == "__main__":
    process_new_assets()
