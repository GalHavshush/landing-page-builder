"""Markdown -> sanitised HTML. Raw HTML in the source is escaped, output is cleaned again."""

import nh3
from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark", {"html": False, "linkify": False})


def render_markdown(source: str) -> str:
    return nh3.clean(_md.render(source or ""))
