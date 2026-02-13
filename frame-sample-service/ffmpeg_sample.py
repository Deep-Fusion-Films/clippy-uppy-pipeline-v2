import os
import subprocess
from utils import log, generate_id

MAX_FRAMES = 50


def extract_frames(input_path: str, output_dir: str):
    """
    Extracts frames at 1 FPS, capped at 50 frames.
    """

    os.makedirs(output_dir, exist_ok=True)

    # FFmpeg command: 1 FPS, output as frame_0001.jpg etc.
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "fps=1",
        f"{output_dir}/frame_%04d.jpg",
        "-y"
    ]

    log("Running FFmpeg frame extraction", command=" ".join(command))

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {process.stderr.decode()}")

    # Cap at 50 frames
    frames = sorted(os.listdir(output_dir))
    if len(frames) > MAX_FRAMES:
        for f in frames[MAX_FRAMES:]:
            os.remove(os.path.join(output_dir, f))
        frames = frames[:MAX_FRAMES]

    log("Frame extraction complete", frame_count=len(frames))

    return frames

