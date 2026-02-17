import os
import json
from typing import List

from google.cloud import pubsub_v1
from newsflare_api import NewsflareClient
from cross_cloud_transfer import transfer_to_gcs

PROJECT_ID = os.environ["PROJECT_ID"]
PUBSUB_TOPIC = os.environ["INGEST_TOPIC"]
GCS_RAW_BUCKET = os.environ["RAW_VIDEO_BUCKET"]
GCS_SOURCE_PREFIX = "newsflare"


def publish_asset_event(publisher: pubsub_v1.PublisherClient, asset_id: str, gcs_uri: str):
    message = {
        "asset_id": asset_id,
        "source": "newsflare",
        "video_uri": gcs_uri,
    }
    data = json.dumps(message).encode("utf-8")
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
    future = publisher.publish(topic_path, data=data)
    future.result()


def process_new_assets():
    client = NewsflareClient(
        api_key=os.environ["NEWSFLARE_API_KEY"],
    )
    publisher = pubsub_v1.PublisherClient()

    assets = client.list_new_videos()
    for asset in assets:
        asset_id = asset["id"]
        remote_url = asset["video_url"]

        object_name = f"{GCS_SOURCE_PREFIX}/{asset_id}.mp4"
        gcs_uri = transfer_to_gcs(remote_url, GCS_RAW_BUCKET, object_name)

        publish_asset_event(publisher, asset_id, gcs_uri)


def main(request=None):
    process_new_assets()
    return ("OK", 200)


if __name__ == "__main__":
    process_new_assets()

