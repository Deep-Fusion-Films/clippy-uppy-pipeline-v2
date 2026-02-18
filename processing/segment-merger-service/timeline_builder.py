def build_timeline(transcripts: dict, vision: dict) -> list:
    """
    Produces a simple timeline structure combining transcript + vision per segment.
    """

    timeline = []
    for idx in sorted(int(k) for k in transcripts.keys()):
        timeline.append(
            {
                "segment_index": idx,
                "transcript": transcripts[str(idx)],
                "vision": vision[str(idx)],
            }
        )

    return timeline
