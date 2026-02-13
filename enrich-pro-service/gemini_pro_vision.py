import base64
from typing import List
from google import genai
from utils import log
from schema_pro import ClipMetadataPro
from prompt_pro import build_pro_prompt
import json


def load_image_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def call_gemini_pro_vision(transcript: str, frame_paths: List[str]) -> ClipMetadataPro:
    client = genai.Client()

    prompt = build_pro_prompt(transcript)

    parts = [{"text": prompt}]

    for frame_path in frame_paths:
        img_bytes = load_image_bytes(frame_path)
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_bytes).decode("utf-8"),
            }
        })

    log("Calling Gemini Pro Vision", frame_count=len(frame_paths))

    response = client.models.generate_content(
        model="gemini-1.5-pro-vision",
        contents=parts,
        config={
            "response_mime_type": "application/json",
        },
    )

    raw_text = response.text
    log("Received response from Gemini Pro Vision", length=len(raw_text))

    data = json.loads(raw_text)
    metadata = ClipMetadataPro(**data)
    metadata.raw_model_output = data
    return metadata

