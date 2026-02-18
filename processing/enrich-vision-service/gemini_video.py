import tempfile
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from prompt import VISION_PROMPT


def _download_segment(uri: str) -> str:
    """Download a GCS video segment to a temporary local file."""
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    fd, local_path = tempfile.mkstemp(suffix=".mp4")
    blob.download_to_filename(local_path)
    return local_path


# -----------------------------
# NEW STRUCTURED OUTPUT CONFIG
# -----------------------------
VISION_GENERATION_CONFIG = GenerationConfig(
    response_mime_type="application/json"
)


def enrich_segment(segment_uri: str) -> dict:
    """Run Gemini 1.5 Flash on a video segment and return structured JSON."""
    video_path = _download_segment(segment_uri)

    model = GenerativeModel("gemini-1.5-flash")

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    # Gemini will return JSON directly because of response_mime_type="application/json"
    response = model.generate_content(
        [
            Part.from_data(video_bytes, mime_type="video/mp4"),
            VISION_PROMPT,  # Your prompt must embed the schema block
        ],
        generation_config=VISION_GENERATION_CONFIG,
    )

    try:
        # response.text contains the raw JSON string
        return response.text
    except Exception as e:
        return {
            "error": f"Failed to parse Gemini response: {str(e)}"
        }
