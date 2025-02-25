from stresolve import util
import argparse
import os
import difflib
import sys
from pathlib import Path
import filecmp


def find_sync_conflicts(directory):
    conflicts = []
    for root, _, files in directory.walk():
        for file in files:
            if ".sync-conflict-" in str(file):
                conflicts.append(root / file)
    return conflicts


def compare_text_files(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        diff = difflib.unified_diff(
            f1.readlines(), f2.readlines(), fromfile=file1, tofile=file2
        )
    return "".join(diff)


def compare_files(file1, file2):
    if util.is_text_file(file1) and util.is_text_file(file2):
        diff = compare_text_files(file1, file2)
    else:
        areSame = filecmp.cmp(file1, file2)
        if areSame:
            diff = "Binary files are identical."
        else:
            diff = "Binary files differ."
    lines = []
    lines.append(diff)
    for file in [file1, file2]:
        stat = file.stat()
        lines.append(f"{file1}:")
        lines.append(f"  Length: {stat.st_size} bytes")
        lines.append(f"  Type: {stat.st_type}")
        lines.append("")

    return "\n".join(lines)


def resolve_conflicts(directory):
    conflicts = find_sync_conflicts(directory)
    for conflict in conflicts:
        original = Path(conflict).with_suffix("")
        print(f"\nConflict found: {conflict}")
        print(f"Original file: {original}")

        diff = compare_files(original, conflict)
        print("\nDifferences:")
        print(diff)

        choice = input(
            "Keep current version (c), use sync conflict (s), or skip (k)? "
        ).lower()
        if choice == "c":
            os.remove(conflict)
            print("Kept current version, removed sync conflict.")
        elif choice == "s":
            os.replace(conflict, original)
            print("Used sync conflict version, replaced original file.")
        elif choice == "k":
            print("Skipped this conflict.")
        else:
            print("Invalid choice, skipping.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    args = ap.parse_args()

    resolve_conflicts(Path(args.dir))


if __name__ == "__main__":
    main()
