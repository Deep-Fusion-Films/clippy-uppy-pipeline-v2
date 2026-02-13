import base64
from utils import log
from google import genai


def transcribe_audio(local_audio_path: str) -> str:
    """
    Sends audio to Gemini Audio for transcription.
    """

    client = genai.Client()

    with open(local_audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    log("Sending audio to Gemini Audio")

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            {
                "mime_type": "audio/wav",
                "data": audio_b64
            }
        ]
    )

    transcript = response.text.strip()
    log("Received transcript", length=len(transcript))

    return transcript

