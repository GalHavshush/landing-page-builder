"""ZIP export (ADR 004): plain static files + README + export.json for re-import."""

import io
import json
import zipfile

from sitegen.posts import Post
from sitegen.schema import SiteDocument

README = """This folder is a complete static website. There is nothing to install.

- Open index.html in a browser to preview it locally.
- To publish, upload the contents of this folder to any static host
  (Cloudflare Pages, Netlify, GitHub Pages, S3, your own web server...).
- export.json (and posts.json, if you have a blog) is the editable source of the site;
  keep them to re-import the site later.
"""

_FIXED_TIME = (2020, 1, 1, 0, 0, 0)  # deterministic archives


def make_zip(files: dict[str, bytes], doc: SiteDocument, posts: list[Post] | None = None) -> bytes:
    extra = {
        "README.txt": README.encode(),
        "export.json": doc.model_dump_json(indent=2).encode(),
    }
    if posts:
        extra["posts.json"] = json.dumps(
            [p.model_dump(mode="json") for p in posts], indent=2, ensure_ascii=False
        ).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted({**files, **extra}.items()):
            info = zipfile.ZipInfo(name, _FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return buf.getvalue()
