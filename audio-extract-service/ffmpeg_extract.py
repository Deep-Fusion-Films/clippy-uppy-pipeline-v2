import subprocess
from utils import log


def extract_audio(input_path: str, output_path: str):
    """
    Extracts audio using FFmpeg in a safe, streaming way.
    Output is always .wav (16-bit PCM).
    """

    command = [
        "ffmpeg",
        "-i", input_path,
        "-vn",               # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",      # 16 kHz for Gemini Audio
        "-ac", "1",          # mono
        output_path,
        "-y"
    ]

    log("Running FFmpeg", command=" ".join(command))

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {process.stderr.decode()}")

    log("Audio extraction complete", output=output_path)

