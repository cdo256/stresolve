import argparse
import os
from pathlib import Path
from termcolor import colored
import subprocess as sp
from stresolve.automerge import merge_if_applicable
from .util import read_and_escape_nonprintable, strip_suffix
from .conflicts import find_sync_conflicts
from .diffing import compare_files


options = {"use_trash": False, "dir": None}


def resolve_conflicts(directory):
    conflicts = find_sync_conflicts(directory)
    for conflict in conflicts:
        original = Path(strip_suffix(conflict))
        print(f"\nConflict found: {conflict}")
        print(f"Original file: {original}")

        diff = compare_files(original, conflict)
        if diff is None:
            print("Files are identical.")
        else:
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
                "additional options: print both (p), open both in another application (n),\n"
                "automerge (m)"
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
            elif choice == "m":
                merge_if_applicable(conflict, options["dir"])
            else:
                print("Invalid choice.")
                continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-trash", "-t", action="store_true")
    ap.add_argument("dir")
    args = ap.parse_args()
    options["use_trash"] = args.use_trash
    options["dir"] = args.dir

    try:
        resolve_conflicts(Path(args.dir))
    except KeyboardInterrupt:
        pass
