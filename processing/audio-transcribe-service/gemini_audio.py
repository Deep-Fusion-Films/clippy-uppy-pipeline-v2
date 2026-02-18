import tempfile
import subprocess
from google.cloud import storage
from vertexai.generative_models import GenerativeModel


def _download_segment(uri: str) -> str:
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    fd, local_path = tempfile.mkstemp(suffix=".mp4")
    blob.download_to_filename(local_path)
    return local_path


def _extract_audio(video_path: str) -> str:
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
    video_path = _download_segment(segment_uri)
    audio_path = _extract_audio(video_path)

    model = GenerativeModel("gemini-1.5-flash")

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    response = model.generate_content(
        [
            {
                "mime_type": "audio/wav",
                "data": audio_bytes,
            },
            "Transcribe this audio accurately."
        ]
    )

    return response.text
