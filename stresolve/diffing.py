import difflib
from termcolor import colored
from .util import read_and_escape_nonprintable


def compare_text_files(file1, file2):
    try:
        file1_contents = read_and_escape_nonprintable(file1)
    except Exception as e:
        raise RuntimeError(
            f"No matching original file {file1} for {file2}: {e!r}"
        ) from e
    file2_contents = read_and_escape_nonprintable(file2)
    diff = difflib.unified_diff(
        list(map(lambda line: line + "\n", file1_contents.splitlines())),
        list(map(lambda line: line + "\n", file2_contents.splitlines())),
        fromfile=str(file1),
        tofile=str(file2),
    )
    return "".join(diff)


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
    try:
        diff = compare_text_files(file1, file2)
        print(f"diff = {diff!r}")
        if len(diff) == 0:
            # Files are identical
            return None
        lines = parse_diff(diff) + [""]
        print(f"lines = {lines!r}")
    except Exception as e:
        lines = [f"diff failed: {e!r}", ""]
        lines.append(colored(f"{file1} (original):", "red"))
        lines.append(colored(f"{file2} (conflict):", "green"))
        lines.append("")
    print(f"final lines = {lines!r}")
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
