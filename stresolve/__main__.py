from stresolve import util
import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    args = ap.parse_args()
    print(util.is_text_file(args.file))


if __name__ == "__main__":
    main()

