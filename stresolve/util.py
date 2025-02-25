import cchardet


def is_text_file(
    filename: str,
    sample_size: int = 1024,
    confidence_threshold: float = 0.7,
    non_text_threshold: float = 0.3,
) -> bool:
    """
    Determines if a file is text or binary using a combination of heuristics and
    statistical encoding detection. Handles Unicode encodings like UTF-8/16/32.

    Args:
        filename: Path to the file
        sample_size: Bytes to read from start/end (default: 1024)
        confidence_threshold: chardet confidence required (default: 0.7)
        non_text_threshold: Max ratio of non-text bytes allowed (default: 0.3)

    Returns:
        True if file is likely text, False if binary
    """
    # Encodings where null bytes are valid (UTF-16/32 variants)
    NULL_ALLOWED_ENCODINGS = {
        "utf-16",
        "utf-16le",
        "utf-16be",
        "utf-32",
        "utf-32le",
        "utf-32be",
    }

    try:
        with open(filename, "rb") as f:
            # Read start and end samples to catch mixed content
            file_size = f.seek(0, 2)
            if file_size == 0:
                return True  # Empty files are text

            # Read start sample
            f.seek(0)
            start_sample = f.read(min(sample_size, file_size))

            # Read end sample if file is larger than sample_size
            end_sample = b""
            if file_size > sample_size:
                f.seek(-sample_size, 2)
                end_sample = f.read(sample_size)

            combined_sample = start_sample + end_sample
    except (IOError, OSError):
        return False

    # Detect encoding early to handle null-byte exceptions
    detection = cchardet.detect(combined_sample)
    print("detection:", detection)
    try:
        encoding = detection.get("encoding", "").lower()
        confidence = detection.get("confidence", 0.0)
    except AttributeError:
        encoding = "binrary"
        confidence = 1.0

    # Null byte check logic
    skip_null_check = (
        confidence >= confidence_threshold and encoding in NULL_ALLOWED_ENCODINGS
    )
    if not skip_null_check:
        if b"\x00" in combined_sample:
            return False  # Binary files contain raw nulls

    # High-confidence encoding match
    if confidence >= confidence_threshold and encoding:
        return True  # Valid text encoding detected

    # Heuristic: Allow ASCII control chars + printables
    allowed_bytes = bytes([7, 8, 9, 10, 12, 13, 27]) + bytes(range(32, 127))
    non_text = combined_sample.translate(None, delete=allowed_bytes)
    ratio = len(non_text) / len(combined_sample) if combined_sample else 0

    return ratio <= non_text_threshold
