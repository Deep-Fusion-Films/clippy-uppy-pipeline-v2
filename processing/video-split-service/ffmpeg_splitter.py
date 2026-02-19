import os
import subprocess
import uuid
from google.cloud import storage


MAX_DURATION_SECONDS = 1800  # 30 minutes
MAX_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2GB

storage_client = storage.Client()


def _extract_filename(gs_uri: str) -> str:
    return os.path.basename(gs_uri)


# -------------------------------
# Download GCS → /tmp (required for ffprobe + ffmpeg)
# -------------------------------
def _download_to_tmp(gs_uri: str) -> str:
    bucket_name = gs_uri.split("/")[2]
    object_name = "/".join(gs_uri.split("/")[3:])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    # keep original name but avoid collisions with a UUID prefix
    original = _extract_filename(gs_uri)
    local_path = f"/tmp/{uuid.uuid4()}_{original}"
    blob.download_to_filename(local_path)

    return local_path


# -------------------------------
# Probe duration using local file (strict, never None)
# -------------------------------
def _probe_duration(uri: str) -> float:
    local_path = _download_to_tmp(uri)

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        local_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if not result.stdout.strip():
        # force a clear failure instead of falling through as None
        raise RuntimeError(
            f"ffprobe returned no duration for {uri}. stderr={result.stderr}"
        )

    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError(
            f"ffprobe returned invalid duration for {uri}: '{result.stdout}'"
        )

# -------------------------------
# Probe size directly from GCS
# -------------------------------
def _probe_size(uri: str) -> int:
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])
    blob = storage_client.bucket(bucket_name).blob(object_name)
    return blob.size


# -------------------------------
# Decide whether splitting is needed (safe)
# -------------------------------
def needs_splitting(uri: str) -> bool:
    # _probe_duration will now either return a float or raise
    duration = _probe_duration(uri)
    size = _probe_size(uri)

    return duration > MAX_DURATION_SECONDS or size > MAX_SIZE_BYTES

# -------------------------------
# Split video into 30s segments
# -------------------------------
def split_video(uri: str):
    """
    Splits video into 30-second segments.
    Uploads each segment to GCS.
    Returns list of GCS URIs.
    """
    bucket_name = uri.split("/")[2]
    object_path = "/".join(uri.split("/")[3:])
    base_prefix = object_path.rsplit(".", 1)[0]
    original_name = _extract_filename(uri).rsplit(".", 1)[0]

    bucket = storage_client.bucket(bucket_name)

    # Download full file to /tmp for splitting
    local_path = _download_to_tmp(uri)

    # Prepare segment pattern
    segment_pattern = local_path.rsplit(".", 1)[0] + "_%03d.mp4"

    # Run ffmpeg split
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

        seg_name = f"{base_prefix}/segments/{original_name}_{idx:03d}.mp4"
        seg_blob = bucket.blob(seg_name)
        seg_blob.upload_from_filename(seg_path)

        segments.append(f"gs://{bucket_name}/{seg_name}")
        idx += 1

    return segments
