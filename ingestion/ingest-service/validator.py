def validate_ingest_message(msg: dict):
    required = ["asset_id", "source", "video_uri"]

    for field in required:
        if field not in msg:
            raise ValueError(f"Missing required field: {field}")

    if not msg["video_uri"].startswith("gs://"):
        raise ValueError("video_uri must be a GCS URI")

    if msg["source"] not in ("getty", "newsflare", "uploads"):
        raise ValueError("Invalid source type")
