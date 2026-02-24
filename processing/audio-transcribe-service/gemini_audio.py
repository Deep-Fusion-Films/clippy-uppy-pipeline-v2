import os
import tempfile
import subprocess

from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content


# --- Vertex AI initialisation ---
# Gemini models ONLY exist in us-central1
vertexai.init(
    project="deepfusion-clippyuppy-pipeline",
    location="us-central1"
)


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


def _extract_audio(video_path: str) -> str:
    """Extract mono 16 kHz WAV audio from the video using ffmpeg."""
    audio_path = video_path.replace(".mp4", ".wav")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    subprocess.run(cmd, check=True)
    return audio_path


def transcribe_audio(segment_uri: str) -> str:
    """Download, extract audio, and transcribe using Gemini 1.5 Flash."""
    video_path = _download_segment(segment_uri)
    audio_path = _extract_audio(video_path)

    # Correct model name
    model = GenerativeModel("gemini-1.5-flash-001")

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_part = Part.from_data(
        mime_type="audio/wav",
        data=audio_bytes
    )

    content = Content(
        role="user",
        parts=[
            audio_part,
            Part.from_text("Transcribe this audio accurately.")
        ]
    )

    response = model.generate_content([content])
    return response.text
