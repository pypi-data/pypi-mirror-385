#!/usr/bin/python
# This is from this repo: https://github.com/sharst/seratopy
import os
import sys

if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from serato_tools.utils.crate_base import CrateBase
from serato_tools.utils import SERATO_DIR


class Crate(CrateBase):
    EXTENSION = ".crate"
    DIR = "Subcrates"
    DIR_PATH = os.path.join(SERATO_DIR, DIR)
    SERATO_STEMS_CRATE_PATH = os.path.join(DIR, "Serato Stems", "Stems.crate")

    DEFAULT_ENTRIES = [
        (CrateBase.Fields.VERSION, "1.0/Serato ScratchLive Crate"),
        (CrateBase.Fields.SORTING, [(CrateBase.Fields.COLUMN_NAME, "key"), (CrateBase.Fields.REVERSE_ORDER, False)]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "song"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "playCount"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "artist"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "bpm"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "key"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "album"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "length"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "comment"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
        (CrateBase.Fields.COLUMN, [(CrateBase.Fields.COLUMN_NAME, "added"), (CrateBase.Fields.COLUMN_WIDTH, "0")]),
    ]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_or_dir", nargs="?", help="Set the crate file, or a directory to do all files in it")
    parser.add_argument("--all", action="store_true", help="Perform actions on all crates.")
    parser.add_argument("-l", "--list_tracks", action="store_true", help="Only list tracks")
    parser.add_argument("-f", "--filenames_only", action="store_true", help="Only list track filenames")
    parser.add_argument("--find_missing", action="store_true", help="List files that do not exist")
    args = parser.parse_args()

    if args.all:
        args.file_or_dir = Crate.DIR_PATH

    if not args.file_or_dir:
        print(f"must pass a file or dir, or --all!\nfiles in {Crate.DIR_PATH}:")
        print("\n".join(Crate.get_serato_crate_files()))
        sys.exit()

    for crate_path in Crate.get_serato_crate_files(args.file_or_dir):
        crate = Crate(crate_path)
        if args.find_missing:
            crate.find_missing()
        elif args.list_tracks or args.filenames_only:
            crate.print_track_paths(filenames_only=args.filenames_only)
        else:
            print(crate)


if __name__ == "__main__":
    main()
