import io

import pytest
from app.assets.images import InvalidImage, process_image
from helpers import image_bytes
from PIL import Image


def decode(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_png_becomes_webp_and_keeps_alpha():
    out = process_image(image_bytes("PNG", (40, 30), (10, 20, 30, 128)))
    img = decode(out.main)
    assert img.format == "WEBP" and img.size == (40, 30)
    assert "A" in img.getbands()
    assert (out.width, out.height) == (40, 30)


def test_large_images_are_downscaled_and_get_srcset_variants():
    out = process_image(image_bytes("JPEG", (3000, 1500), mode="RGB"))
    assert decode(out.main).size == (2400, 1200)
    assert [w for w, _ in out.variants] == [320, 640, 960, 1440]
    for width, data in out.variants:
        assert decode(data).size[0] == width  # aspect ratio kept
    assert out.thumb == out.variants[0][1]  # the 320px copy is the editor thumbnail
    assert (out.width, out.height) == (2400, 1200)
    assert [len(d) for _, d in out.variants] == sorted(
        len(d) for _, d in out.variants
    )  # smaller is lighter


def test_variants_are_only_made_for_widths_below_the_main_file():
    out = process_image(image_bytes("PNG", (700, 400)))
    assert [w for w, _ in out.variants] == [320, 640]
    assert process_image(image_bytes("PNG", (300, 200))).variants == []


def test_very_tall_images_are_height_limited():
    out = process_image(image_bytes("PNG", (800, 9000), mode="RGB"))
    assert out.height <= 3600


def test_average_colour_is_reported_as_hex():
    out = process_image(image_bytes("PNG", (50, 50), (200, 40, 40, 255)))
    assert out.color == "#c82828"


def test_small_images_are_not_upscaled():
    assert decode(process_image(image_bytes("PNG", (10, 10))).main).size == (10, 10)


def test_exif_is_stripped_and_rotation_applied():
    data = image_bytes("JPEG", (40, 20), mode="RGB", exif_orientation=6)  # rotated 90 degrees
    out = process_image(data)
    img = decode(out.main)
    assert img.size == (20, 40)  # orientation honoured
    assert not img.getexif()  # camera metadata gone
    assert b"SecretCameraMaker" not in out.main


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"not an image",
        b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>",
    ],
)
def test_garbage_and_svg_are_rejected(data):
    with pytest.raises(InvalidImage):
        process_image(data)


def test_gif_is_rejected():
    with pytest.raises(InvalidImage, match="JPEG, PNG and WebP"):
        process_image(image_bytes("GIF", mode="RGB"))


def test_truncated_image_is_rejected():
    with pytest.raises(InvalidImage):
        process_image(image_bytes("PNG", (200, 200))[:60])
