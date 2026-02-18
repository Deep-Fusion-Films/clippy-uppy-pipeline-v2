def merge_segments(transcripts: dict, vision: dict) -> dict:
    """
    transcripts: { "0": "...", "1": "...", ... }
    vision: { "0": "...", "1": "...", ... }

    Returns:
    {
        "transcript": "...",
        "vision": [...]
    }
    """

    # Merge transcripts in order
    ordered_transcripts = [
        transcripts[str(i)] for i in sorted(int(k) for k in transcripts.keys())
    ]
    full_transcript = "\n".join(ordered_transcripts)

    # Merge vision metadata in order
    ordered_vision = [
        vision[str(i)] for i in sorted(int(k) for k in vision.keys())
    ]

    return {
        "transcript": full_transcript,
        "vision": ordered_vision,
    }
