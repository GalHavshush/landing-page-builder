"""Command line: build a site from a JSON document, no server or database needed.

python -m sitegen build site.json out/ [--zip site.zip]
python -m sitegen init clean site.json
python -m sitegen validate site.json
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from sitegen.builder import build
from sitegen.export import make_zip
from sitegen.schema import SiteDocument
from sitegen.starters import list_starters, load_starter


def _load(path: str) -> SiteDocument:
    return SiteDocument.model_validate(json.loads(Path(path).read_text()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sitegen")
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build a site into a folder (and optionally a ZIP)")
    b.add_argument("document")
    b.add_argument("out")
    b.add_argument("--zip", dest="zip_path")
    i = sub.add_parser("init", help="write a starter document")
    i.add_argument("starter", choices=list_starters())
    i.add_argument("document")
    i.add_argument("--name")
    v = sub.add_parser("validate", help="validate a document")
    v.add_argument("document")
    args = parser.parse_args(argv)

    if args.cmd == "init":
        doc = load_starter(args.starter, args.name)
        Path(args.document).write_text(doc.model_dump_json(indent=2))
        print(f"wrote {args.document}")
        return 0
    try:
        doc = _load(args.document)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    if args.cmd == "validate":
        print("ok")
        return 0
    result = build(doc)
    out = Path(args.out)
    for path, data in result.files.items():
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    if args.zip_path:
        Path(args.zip_path).write_bytes(make_zip(result.files, doc))
    for issue in result.issues:
        print(f"{issue.level}: {issue.message}", file=sys.stderr)
    print(f"built {len(result.files)} files into {out}")
    return 0
