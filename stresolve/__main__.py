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


def find_sync_conflicts(directory):
    conflicts = []
    for root, _, files in directory.walk():
        for file in files:
            if ".sync-conflict-" in str(file):
                conflicts.append(root / file)
    return conflicts


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


def compare_text_files(file1, file2):
    try:
        file1_contents = read_and_escape_nonprintable(file1)
    except Exception as e:
        print(f"No matching original file {file1} for {file2}.")
        print(e)
        do_remove = typer.confirm(f"Remove {file2}?")
        if do_remove:
            os.remove(file2)
        return None
    file2_contents = read_and_escape_nonprintable(file2)
    diff = difflib.unified_diff(
        list(map(lambda line: line + "\n", file1_contents.splitlines())),
        list(map(lambda line: line + "\n", file2_contents.splitlines())),
        fromfile=str(file1),
        tofile=str(file2),
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
    diff = compare_text_files(file1, file2)
    if diff:
        lines = parse_diff(diff) + [""]
    else:
        lines = ["diff failed.", ""]
        lines.append(colored(f"{file1} (original):", "red"))
        lines.append(colored(f"{file2} (conflict):", "green"))
        lines.append("")
        return lines

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
            print(
                colored("Keep original (o)", "red")
                + ", "
                + colored("use sync conflict (c)", "green")
                + ", or skip (k)?"
            )
            print(
                "additional options: print both (p), open both in another application (n)"
            )
            choice = input("> ").lower()
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
            elif choice == "p":
                print("Original:")
                text = read_and_escape_nonprintable(original)
                print(colored(text, "red"))
                print()
                print("Conflicted version:")
                text = read_and_escape_nonprintable(conflict)
                print(colored(text, "green"))
                print()
                continue
            elif choice == "n":
                sp.run(["xdg-open", original])
                sp.run(["xdg-open", conflict])
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
