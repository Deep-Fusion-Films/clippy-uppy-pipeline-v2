import os
import json
import time
from typing import List

from google.cloud import pubsub_v1
from window_manager import chunk_list, wait_for_window_completion
from gcs_scanner import list_videos_in_folder

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
if __name__ == "__main__":
    start_health_server()

# -------------------------------


PROJECT_ID = os.environ["PROJECT_ID"]
INGEST_TOPIC = os.environ["INGEST_TOPIC"]
WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE", "25"))


def publish_asset_event(publisher, asset_id, source, gcs_uri):
    message = {
        "asset_id": asset_id,
        "source": source,
        "video_uri": gcs_uri,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, INGEST_TOPIC)
    publisher.publish(topic_path, data=data).result()


def process_folder(folder_uri: str):
    """
    folder_uri example:
    gs://raw-videos/getty/2026/02/17/
    gs://raw-videos/newsflare/2026/02/17/
    gs://raw-videos/uploads/2026/02/17/
    """

    publisher = pubsub_v1.PublisherClient()

    videos = list_videos_in_folder(folder_uri)
    if not videos:
        return "No videos found."

    # Infer source from folder path
    # e.g. gs://raw-videos/getty/... → "getty"
    source = folder_uri.split("/")[3]

    windows = chunk_list(videos, WINDOW_SIZE)

    for window in windows:
        for asset in window:
            publish_asset_event(
                publisher,
                asset_id=asset["asset_id"],
                source=source,
                gcs_uri=asset["gcs_uri"],
            )

        # Wait for all assets in this window to complete
        wait_for_window_completion([v["asset_id"] for v in window])

    return "Batch processing complete."


def main(request):
    data = request.get_json()
    folder_uri = data["folder_uri"]
    result = process_folder(folder_uri)
    return (result, 200)
