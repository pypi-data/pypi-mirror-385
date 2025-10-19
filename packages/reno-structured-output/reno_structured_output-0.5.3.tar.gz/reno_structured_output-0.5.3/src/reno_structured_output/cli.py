"""Commandline interface to extract reno notes in machine-readable itemized form."""

import argparse
import json
import logging
import sys

from reno_structured_output import Config, collect_notes

parser = argparse.ArgumentParser(
    prog="reno-structured-output",
    description="Provide 'reno' release notes in machine-readable, itemized form.",
)

parser.add_argument(
    "reporoot",
    nargs="?",
    default="./",
    help="root of the git repository",
)
parser.add_argument(
    "-d",
    "--rel-notes-dir",
    help="location of release notes YAML files (relative to reporoot)",
)
parser.add_argument(
    "-p", "--pretty", action="store_true", help="pretty-print JSON output"
)
parser.add_argument("-v", "--verbose", action="count", default=0)
parser.add_argument("-q", "--quieter", action="count", default=0)


def main() -> int:
    args = parser.parse_args()
    logging.basicConfig(
        level=dict(
            enumerate((logging.ERROR, logging.WARNING, logging.INFO), start=-1)
        ).get(args.verbose - args.quieter, logging.DEBUG)
    )
    print(args, file=sys.stderr)
    config = Config(args.reporoot, relnotesdir=args.rel_notes_dir)
    structured_notes = collect_notes(config)
    indent = 2 if args.pretty else None
    print(json.dumps(structured_notes, indent=indent, sort_keys=False))
    return 0
