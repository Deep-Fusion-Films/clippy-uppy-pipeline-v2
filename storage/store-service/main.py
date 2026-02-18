import os
import json
from google.cloud import storage, firestore

from gcs_writer import write_metadata_to_gcs
from retention_tags import apply_retention_tag

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


db = firestore.Client()

def main(event, context):
    msg = json.loads(event["data"].decode("utf-8"))

    asset_id = msg["asset_id"]
    source = msg["source"]

    # Fetch final metadata from Firestore
    final_doc = db.collection("final").document(asset_id).get()
    if not final_doc.exists:
        return

    final_metadata = final_doc.to_dict()

    # Determine GCS path based on source
    bucket_name = os.environ["METADATA_BUCKET"]
    object_name = f"{source}/{asset_id}.json"

    # Write metadata to GCS
    gcs_uri = write_metadata_to_gcs(bucket_name, object_name, final_metadata)

    # Apply retention tag (30 days)
    apply_retention_tag(bucket_name, object_name)

    # Mark asset as fully completed
    db.collection("assets").document(asset_id).set(
        {"status": "stored", "metadata_uri": gcs_uri},
        merge=True,
    )

