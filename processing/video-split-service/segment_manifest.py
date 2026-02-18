from google.cloud import firestore

db = firestore.Client()


def write_manifest(asset_id: str, segments: list):
    """
    Stores the list of segment URIs so the merger can reassemble them.
    """
    doc = db.collection("manifests").document(asset_id)
    doc.set({"segments": segments}, merge=True)
