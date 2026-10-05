"""A plain share image (1200x630) for sites without one: name and tagline on the brand colour."""

import io

from PIL import Image, ImageDraw, ImageFont
from sitegen.schema import SiteDocument
from sitegen.theme import readable_on

W, H = 1200, 630
MARGIN = 90


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except (TypeError, OSError):  # very old Pillow or no FreeType: still draw something
        return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .,;") + "…"
    return lines


def social_card(doc: SiteDocument) -> bytes:
    p = doc.theme.palette
    bg, fg = p["primary"], readable_on(p["primary"])
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([MARGIN, MARGIN, MARGIN + 90, MARGIN + 8], fill=p["accent"])
    title_font, tag_font = _font(96), _font(40)
    title = _wrap(draw, doc.site.name, title_font, W - 2 * MARGIN, 3)
    y = MARGIN + 70
    for line in title:
        draw.text((MARGIN, y), line, font=title_font, fill=fg)
        y += 112
    tagline = doc.site.tagline or doc.site.seo.default_description
    if tagline:
        y += 14
        for line in _wrap(draw, tagline, tag_font, W - 2 * MARGIN, 2):
            draw.text((MARGIN, y), line, font=tag_font, fill=fg)
            y += 54
    out = io.BytesIO()
    img.save(out, "PNG", optimize=True)
    return out.getvalue()
