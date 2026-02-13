import base64
from typing import List
from google import genai
from utils import log
from schema import ClipMetadata
from prompt import build_prompt
import json


def load_image_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def call_gemini_flash(transcript: str, frame_paths: List[str]) -> ClipMetadata:
    client = genai.Client()

    prompt = build_prompt(transcript)

    parts = [{"text": prompt}]

    for frame_path in frame_paths:
        img_bytes = load_image_bytes(frame_path)
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_bytes).decode("utf-8"),
            }
        })

    log("Calling Gemini Flash", frame_count=len(frame_paths))

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=parts,
        config={
            "response_mime_type": "application/json",
        },
    )

    raw_text = response.text
    log("Received response from Gemini Flash", length=len(raw_text))

    try:
        data = json.loads(raw_text)
    except Exception:
        # If model returns slightly messy JSON, you can add cleanup here later
        raise

    metadata = ClipMetadata(**data)
    metadata.raw_model_output = data
    return metadata

