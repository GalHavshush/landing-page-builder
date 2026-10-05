"""Build every starter, plus a "hostile" copy with awkward content, for the visual QA run.

    uv run python qa/build_sites.py qa/out

Hostile copy: very long headings, long unbroken words, and right-to-left text, to catch overflow.
"""

import copy
import json
import sys
from pathlib import Path

from sitegen import SiteDocument, build
from sitegen.starters import list_starters, load_starter

LONG_WORD = "Supercalifragilisticexpialidocious" * 2
TEXT_KEYS = {
    "heading",
    "title",
    "name",
    "text",
    "description",
    "quote",
    "label",
    "subheading",
    "role",
}


def hostile(node):
    if isinstance(node, dict):
        return {
            k: (
                f"{LONG_WORD} " + v + " " + "lorem ipsum " * 12
                if k in TEXT_KEYS and isinstance(v, str) and v
                else hostile(v)
            )
            for k, v in node.items()
        }
    if isinstance(node, list):
        return [hostile(v) for v in node]
    return node


def write(out: Path, name: str, doc: SiteDocument) -> None:
    for path, data in build(doc).files.items():
        target = out / name / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def main(out: Path) -> None:
    sites = []
    for name in list_starters():
        doc = load_starter(name)
        write(out, name, doc)
        sites.append(name)
        raw = copy.deepcopy(doc.model_dump(mode="json"))
        raw["pages"] = hostile(raw["pages"])
        raw["site"]["name"] = "Name " + LONG_WORD
        write(out, f"{name}--hostile", SiteDocument.model_validate(raw))
        sites.append(f"{name}--hostile")
        # the same site read right-to-left, with mirrored layout
        rtl = copy.deepcopy(doc.model_dump(mode="json"))
        rtl["site"]["languages"] = ["he"]
        rtl["site"]["default_language"] = "he"
        write(out, f"{name}--rtl", SiteDocument.model_validate(rtl))
        sites.append(f"{name}--rtl")
    (out / "sites.json").write_text(json.dumps(sites))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "qa/out"))
