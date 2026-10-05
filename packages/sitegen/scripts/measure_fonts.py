"""Measure each bundled font against Arial/Times and store the result in manifest.json.

Run after adding a font:  uv run --with fonttools --with brotli python scripts/measure_fonts.py
The numbers feed a "<Font> Fallback" @font-face (size-adjust + metric overrides) so text set in a
system font while the real one loads takes the same space, and the page does not jump when it swaps.
"""

import json
from pathlib import Path

from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent.parent / "sitegen" / "static" / "fonts"
# lowercase letter frequencies in English running text (%), plus space
FREQ = dict(
    zip(
        "etaoinshrdlcumwfgypbvkjxqz",
        [
            12.7,
            9.1,
            8.2,
            7.5,
            7.0,
            6.7,
            6.3,
            6.1,
            6.0,
            4.3,
            4.0,
            2.8,
            2.8,
            2.4,
            2.4,
            2.2,
            2.0,
            2.0,
            1.9,
            1.5,
            1.0,
            0.8,
            0.15,
            0.15,
            0.1,
            0.07,
        ],
        strict=True,
    )
)
FREQ[" "] = 18.0
REFERENCE = {
    "sans": ("Arial", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    "serif": (
        "Times New Roman",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ),
}


def avg_width(font: TTFont) -> float:
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return sum(hmtx[cmap[ord(ch)]][0] / upm * w for ch, w in FREQ.items() if ord(ch) in cmap) / sum(
        FREQ.values()
    )


def main() -> None:
    path = FONTS / "manifest.json"
    manifest = json.loads(path.read_text())
    for key, entry in manifest.items():
        font = TTFont(FONTS / key / "latin.woff2")
        upm, hhea = font["head"].unitsPerEm, font["hhea"]
        local, ref_path = REFERENCE[entry["kind"]]
        size = round(avg_width(font) / avg_width(TTFont(ref_path)) * 100, 2)
        scale = size / 100
        entry["metrics"] = {
            "local": local,
            "size_adjust": size,
            "ascent": round(hhea.ascent / upm / scale * 100, 2),
            "descent": round(abs(hhea.descent) / upm / scale * 100, 2),
            "line_gap": round(hhea.lineGap / upm / scale * 100, 2),
        }
        print(key, entry["metrics"])
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
