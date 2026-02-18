import tempfile
from google.cloud import storage
from vertexai.generative_models import GenerativeModel
from prompt import VISION_PROMPT


def _download_segment(uri: str) -> str:
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    fd, local_path = tempfile.mkstemp(suffix=".mp4")
    blob.download_to_filename(local_path)
    return local_path


def enrich_segment(segment_uri: str) -> dict:
    video_path = _download_segment(segment_uri)

    model = GenerativeModel("gemini-1.5-flash")

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    response = model.generate_content(
        [
            {
                "mime_type": "video/mp4",
                "data": video_bytes,
            },
            VISION_PROMPT
        ]
    )

    return response.candidates[0].content.parts[0].text
