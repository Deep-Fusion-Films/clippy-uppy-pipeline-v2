import tempfile
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part, Schema
from prompt import VISION_PROMPT


def _download_segment(uri: str) -> str:
    bucket_name = uri.split("/")[2]
    object_name = "/".join(uri.split("/")[3:])

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)

    fd, local_path = tempfile.mkstemp(suffix=".mp4")
    blob.download_to_filename(local_path)
    return local_path


VISION_SCHEMA = Schema(
    type=Schema.Type.OBJECT,
    properties={
        "brief_summary": Schema(type=Schema.Type.STRING),
        "verbose_summary": Schema(type=Schema.Type.STRING),

        "people": Schema(
            type=Schema.Type.OBJECT,
            properties={
                "present": Schema(type=Schema.Type.BOOLEAN),
                "count": Schema(type=Schema.Type.NUMBER, nullable=True),
                "details": Schema(
                    type=Schema.Type.ARRAY,
                    items=Schema(
                        type=Schema.Type.OBJECT,
                        properties={
                            "age": Schema(type=Schema.Type.STRING, nullable=True),
                            "gen": Schema(type=Schema.Type.STRING, nullable=True),
                            "role": Schema(type=Schema.Type.STRING, nullable=True),
                            "act": Schema(
                                type=Schema.Type.ARRAY,
                                items=Schema(type=Schema.Type.STRING)
                            ),
                            "pos": Schema(type=Schema.Type.STRING, nullable=True),
                            "clo": Schema(
                                type=Schema.Type.ARRAY,
                                items=Schema(type=Schema.Type.STRING)
                            ),
                            "vis": Schema(type=Schema.Type.STRING, nullable=True),
                        },
                    ),
                ),
            },
        ),

        "animals": Schema(
            type=Schema.Type.ARRAY,
            items=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "type": Schema(type=Schema.Type.STRING),
                    "cnt": Schema(type=Schema.Type.NUMBER, nullable=True),
                    "beh": Schema(
                        type=Schema.Type.ARRAY,
                        items=Schema(type=Schema.Type.STRING)
                    ),
                    "col": Schema(type=Schema.Type.STRING, nullable=True),
                    "pos": Schema(type=Schema.Type.STRING, nullable=True),
                    "int": Schema(
                        type=Schema.Type.ARRAY,
                        items=Schema(type=Schema.Type.STRING)
                    ),
                },
            ),
        ),

        "objects": Schema(
            type=Schema.Type.ARRAY,
            items=Schema(
                type=Schema.Type.OBJECT,
                properties={
                    "lbl": Schema(type=Schema.Type.STRING),
                    "cnt": Schema(type=Schema.Type.NUMBER, nullable=True),
                    "sal": Schema(type=Schema.Type.NUMBER, nullable=True),
                    "pos": Schema(type=Schema.Type.STRING, nullable=True),
                    "use": Schema(type=Schema.Type.STRING, nullable=True),
                    "col": Schema(type=Schema.Type.STRING, nullable=True),
                    "txt": Schema(
                        type=Schema.Type.OBJECT,
                        properties={
                            "orig": Schema(type=Schema.Type.STRING, nullable=True),
                            "lang": Schema(type=Schema.Type.STRING, nullable=True),
                            "eng": Schema(type=Schema.Type.STRING, nullable=True),
                        },
                    ),
                },
            ),
        ),

        "brand_ip": Schema(
            type=Schema.Type.OBJECT,
            properties={
                "logos": Schema(type=Schema.Type.ARRAY, items=Schema(type=Schema.Type.STRING)),
                "other": Schema(type=Schema.Type.ARRAY, items=Schema(type=Schema.Type.STRING)),
                "ctx": Schema(type=Schema.Type.STRING, nullable=True),
            },
        ),

        "celebrities": Schema(
            type=Schema.Type.OBJECT,
            properties={
                "detected": Schema(type=Schema.Type.ARRAY, items=Schema(type=Schema.Type.STRING)),
                "ctx": Schema(type=Schema.Type.STRING, nullable=True),
            },
        ),

        "camera": Schema(type=Schema.Type.OBJECT),
        "environment": Schema(type=Schema.Type.OBJECT),
        "audio": Schema(type=Schema.Type.OBJECT),
        "text_overlays": Schema(type=Schema.Type.OBJECT),
        "quick_edits": Schema(type=Schema.Type.OBJECT),
        "timeline": Schema(type=Schema.Type.ARRAY, items=Schema(type=Schema.Type.OBJECT)),
        "recognizable": Schema(type=Schema.Type.OBJECT),
        "historical_context": Schema(type=Schema.Type.OBJECT),
        "tags": Schema(type=Schema.Type.ARRAY, items=Schema(type=Schema.Type.STRING)),
        "ai_artifacts": Schema(type=Schema.Type.OBJECT),
    },
)


def enrich_segment(segment_uri: str) -> dict:
    video_path = _download_segment(segment_uri)

    model = GenerativeModel("gemini-1.5-flash")

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    response = model.generate_content(
        [
            Part.from_data(video_bytes, mime_type="video/mp4"),
            VISION_PROMPT,  # VISION_PROMPT should embed SCHEMA_BLOCK
        ],
        response_schema=VISION_SCHEMA,
    )

    try:
        return response.candidates[0].content.parts[0].as_dict()
    except Exception as e:
        return {
            "error": f"Failed to parse Gemini response: {str(e)}"
        }
