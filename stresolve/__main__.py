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
            f1.readlines(), f2.readlines(), fromfile=str(file1), tofile=str(file2)
        )
    return "".join(diff)


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


def color_diff_line(line):
    line = line.rstrip()
    if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
        color = "blue"
    elif line.startswith("-"):
        color = "red"
    elif line.startswith("+"):
        color = "green"
    else:
        color = "white"
    return colored(line, color)


def parse_diff(diff):
    lines = diff.splitlines()
    return list(map(color_diff_line, lines))


def compare_files(file1, file2):
    if util.is_text_file(file1) and util.is_text_file(file2):
        diff = compare_text_files(file1, file2)
    else:
        areSame = filecmp.cmp(file1, file2)
        if areSame:
            diff = "Binary files are identical."
        else:
            diff = "Binary files differ."
    lines = parse_diff(diff) + [""]
    fstat = file1.stat()
    lines.append(colored(f"{file1} (original):", "red"))
    lines.append(colored(f"  Length: {fstat.st_size} bytes", "red"))
    lines.append(colored(f"  Type: {file_type_from_stat(fstat)}", "red"))
    lines.append("")
    fstat = file2.stat()
    lines.append(colored(f"{file2} (conflict):", "green"))
    lines.append(colored(f"  Length: {fstat.st_size} bytes", "green"))
    lines.append(colored(f"  Type: {file_type_from_stat(fstat)}", "green"))
    lines.append("")

    return lines


def strip_suffix(filename):
    return re.sub(r"\.sync-conflict-\w*-\w*-\w*", "", str(filename))


def resolve_conflicts(directory):
    conflicts = find_sync_conflicts(directory)
    for conflict in conflicts:
        original = Path(strip_suffix(conflict))
        print(f"\nConflict found: {conflict}")
        print(f"Original file: {original}")

        diff = compare_files(original, conflict)
        print("\nDifferences:")
        print("\n".join(diff))

        while True:
            choice = input(
                "Keep original (o), use sync conflict (c), or skip (k)? "
            ).lower()
            if choice == "o":
                os.remove(conflict)
                print("Kept current version, removed sync conflict.")
                break
            elif choice == "c":
                os.replace(conflict, original)
                print("Used sync conflict version, replaced original file.")
                break
            elif choice == "k":
                print("Skipped this conflict.")
                break
            else:
                print("Invalid choice.")
                continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    args = ap.parse_args()

    try:
        resolve_conflicts(Path(args.dir))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
