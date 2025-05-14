from stresolve import util
import argparse
import os
import difflib
import sys
from pathlib import Path
import filecmp
import re
import stat
from termcolor import colored
import string
import typer
import subprocess as sp
from stresolve.automerge import merge_if_applicable

import string
import stat
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


def read_and_escape_nonprintable(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    # Build a string with non-printable characters escaped as hex (\xXX)
    result = ""
    for b in data:
        char = chr(b)
        if char in string.printable or char in "\t\n\r":
            result += char
        else:
            result += "\\x{:02x}".format(b)
    return result


def file_type_from_stat(fstat):
    mode = fstat.st_mode
    if stat.S_ISDIR(mode):
        return "directory"
    elif stat.S_ISREG(mode):
        return "regular file"
    elif stat.S_ISLNK(mode):
        return "symlink"
    elif stat.S_ISCHR(mode):
        return "character device"
    elif stat.S_ISBLK(mode):
        return "block device"
    elif stat.S_ISFIFO(mode):
        return "FIFO/pipe"
    elif stat.S_ISSOCK(mode):
        return "socket"
    else:
        return "unknown"


def do_remove(file):
    if options.use_trash:
        do_remove = typer.confirm(f"Send {file} to trash?")
        if do_remove:
            sp.run(["trash", file])
    else:
        do_remove = typer.confirm(f"Remove {file}?")
        if do_remove:
            os.remove(file)


def strip_suffix(filename):
    return re.sub(r"\.sync-conflict-\w*-\w*-\w*", "", str(filename))
