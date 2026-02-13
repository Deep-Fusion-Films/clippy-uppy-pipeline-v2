from textwrap import dedent


def build_pro_prompt(transcript: str) -> str:
    return dedent(f"""
    You are an expert video analyst.

    You are given:
    - A sequence of frames from a video (ordered in time)
    - The full transcript of the audio

    Your job is to produce rich, structured JSON metadata describing:
    - People (roles, appearance, whether they are speaking)
    - Objects (primary vs background)
    - Environment (location type, setting, time of day, weather)
    - Camera (movement, framing, style, transitions)
    - Timeline events (what happens over time)
    - A concise summary
    - Suggested tags

    Rules:
    - Use only information visible in the frames or present in the transcript.
    - Do not hallucinate specific identities.
    - If unsure, use generic descriptions.
    - Timeline events should describe key changes or actions.
    - Return ONLY valid JSON. No prose, no explanation.

    Transcript:
    {transcript}
    """).strip()

