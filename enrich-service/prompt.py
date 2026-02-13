from textwrap import dedent


def build_prompt(transcript: str) -> str:
    return dedent(f"""
    You are an expert video metadata analyst.

    You are given:
    - A set of frames from a video
    - The full transcript of the audio

    Your job is to produce structured JSON metadata describing:
    - People (names if known, otherwise descriptions)
    - Objects
    - Environment (location type, setting, time of day)
    - Camera (movement, framing, style)
    - A short summary
    - Suggested tags

    Rules:
    - Use only information visible in the frames or present in the transcript.
    - Do not hallucinate specific identities.
    - If unsure, use generic descriptions.
    - Return ONLY valid JSON. No prose, no explanation.

    Transcript:
    {transcript}
    """).strip()

