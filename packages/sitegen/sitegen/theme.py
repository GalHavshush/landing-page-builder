"""Theme tokens -> CSS custom properties. Sections only ever reference the variables."""

from sitegen.fonts import font_stack
from sitegen.schema import Theme

FONT_STACKS = {
    "sans": 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    "serif": '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif',
    "humanist": 'Seravek, "Gill Sans Nova", Ubuntu, Calibri, "DejaVu Sans", sans-serif',
    "rounded": 'ui-rounded, "Hiragino Maru Gothic ProN", Quicksand, Nunito, "Segoe UI", sans-serif',
}
RADII = {"none": "0", "sm": "4px", "md": "10px", "lg": "18px", "full": "999px"}
SPACE_UNIT = {"compact": "3rem", "normal": "4.5rem", "spacious": "6.5rem"}


def _channel(c: int) -> float:
    v = c / 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def readable_on(background: str) -> str:
    """Pick black or white text, whichever contrasts more with `background`."""
    return (
        "#FFFFFF"
        if contrast_ratio(background, "#FFFFFF") >= contrast_ratio(background, "#111111")
        else "#111111"
    )


def theme_css(theme: Theme) -> str:
    p = theme.palette
    return f""":root {{
  --color-primary: {p["primary"]};
  --color-primary-contrast: {readable_on(p["primary"])};
  --color-accent: {p["accent"]};
  --color-bg: {p["background"]};
  --color-surface: {p["surface"]};
  --color-text: {p["text"]};
  --font-heading: {font_stack(theme.fonts["heading"], FONT_STACKS)};
  --font-body: {font_stack(theme.fonts["body"], FONT_STACKS)};
  --radius: {RADII[theme.radius]};
  --space-unit: {SPACE_UNIT[theme.spacing]};
}}
"""
