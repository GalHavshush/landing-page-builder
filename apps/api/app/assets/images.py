"""Turns an untrusted upload into safe, web-ready images.

We never trust the filename or Content-Type: Pillow must be able to decode the bytes as one
of the allowed formats. The image is then *re-encoded* (WebP), which strips EXIF/GPS metadata
and anything smuggled inside the original file (so there is nothing to serve but pixels).
SVG is not accepted (it can carry scripts).
"""

import io
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_PIXELS = 50_000_000  # decompression-bomb guard
MAIN_MAX_SIDE = 2400
# smaller copies for srcset (browsers pick what fits); 320 doubles as the thumbnail
VARIANT_WIDTHS = (320, 640, 960, 1440)

Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class InvalidImage(ValueError):
    pass


@dataclass
class ProcessedImage:
    main: bytes
    thumb: bytes  # the smallest variant (or the main file for tiny pictures)
    width: int
    height: int
    variants: list[tuple[int, bytes]]  # widths strictly smaller than the main file
    color: str  # average colour, used as the placeholder while the picture loads


def _encode(
    img: Image.Image, max_side: int, quality: int, max_height: int = 10**6
) -> tuple[bytes, tuple[int, int]]:
    img = img.copy()
    img.thumbnail((max_side, max_height), Image.Resampling.LANCZOS)  # only ever shrinks
    out = io.BytesIO()
    img.save(out, "WEBP", quality=quality, method=4)
    return out.getvalue(), img.size


def process_image(data: bytes) -> ProcessedImage:
    try:
        with Image.open(io.BytesIO(data)) as probe:
            if probe.format not in ALLOWED_FORMATS:
                raise InvalidImage("Only JPEG, PNG and WebP images are supported")
            probe.verify()  # cheap structural check
        with Image.open(io.BytesIO(data)) as img:
            img = ImageOps.exif_transpose(img)  # honour camera rotation, then drop EXIF
            img = img.convert("RGBA" if "A" in img.getbands() or img.mode == "P" else "RGB")
            main, size = _encode(img, MAIN_MAX_SIDE, 85, max_height=3600)
            variants = []
            for w in VARIANT_WIDTHS:
                if w < size[0]:
                    data, _ = _encode(img, w, 80 if w > 320 else 76)
                    variants.append((w, data))
            thumb = variants[0][1] if variants else main
            r, g, b = img.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    except InvalidImage:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as exc:
        raise InvalidImage("This file is not a valid image") from exc
    return ProcessedImage(
        main=main,
        thumb=thumb,
        width=size[0],
        height=size[1],
        variants=variants,
        color=f"#{r:02x}{g:02x}{b:02x}",
    )
