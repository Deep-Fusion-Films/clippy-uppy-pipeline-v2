from google.cloud import firestore

db = firestore.Client()


def register_asset(asset_id: str, source: str, video_uri: str):
    """
    Creates a Firestore record for tracking the asset through the pipeline.
    """
    doc_ref = db.collection("assets").document(asset_id)
    doc_ref.set(
        {
            "asset_id": asset_id,
            "source": source,
            "video_uri": video_uri,
            "status": "ingested",
        },
        merge=True,
    )
