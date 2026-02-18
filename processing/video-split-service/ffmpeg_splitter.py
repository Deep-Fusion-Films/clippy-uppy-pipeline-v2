import subprocess
import tempfile
import uuid
from google.cloud import storage


MAX_DURATION_SECONDS = 1800  # 30 minutes
MAX_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2GB


def _probe_duration(uri: str) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", uri]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def _probe_size(uri: str) -> int:
    # GCS blob size
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])
    client = storage.Client()
    blob = client.bucket(bucket_name).blob(object_name)
    return blob.size


def needs_splitting(uri: str) -> bool:
    duration = _probe_duration(uri)
    size = _probe_size(uri)
    return duration > MAX_DURATION_SECONDS or size > MAX_SIZE_BYTES


def split_video(uri: str):
    """
    Splits video into 30-second segments.
    Uploads each segment to GCS.
    Returns list of GCS URIs.
    """
    bucket_name = uri.split("/")[2]
    base_prefix = "/".join(uri.split("/")[3:]).rsplit(".", 1)[0]

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Download to temp file
    fd, local_path = tempfile.mkstemp(suffix=".mp4")

    blob = bucket.blob("/".join(uri.split("/")[3:]))
    blob.download_to_filename(local_path)

    # Split using ffmpeg
    segment_pattern = local_path.replace(".mp4", "_%03d.mp4")
    cmd = [
        "ffmpeg", "-i", local_path,
        "-c", "copy",
        "-map", "0",
        "-segment_time", "30",
        "-f", "segment",
        segment_pattern
    ]
    subprocess.run(cmd, check=True)

    # Upload segments
    segments = []
    idx = 0
    while True:
        seg_path = segment_pattern.replace("%03d", f"{idx:03d}")
        try:
            with open(seg_path, "rb"):
                pass
        except FileNotFoundError:
            break

        seg_name = f"{base_prefix}/segments/{idx}.mp4"
        seg_blob = bucket.blob(seg_name)
        seg_blob.upload_from_filename(seg_path)

        segments.append(f"gs://{bucket_name}/{seg_name}")
        idx += 1

    return segments
