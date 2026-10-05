# ADR 003: Static output has no backend

Status: accepted

## Decision
- Contact forms post to a third-party endpoint URL configured per site (Formspree/Web3Forms style), with a `mailto:` fallback. We do not host form submissions in v1.
- Blog content is rendered at build time; a new post appears after the next export.
- YouTube uses a click-to-load facade on youtube-nocookie.com. Maps are iframes.
- SVG uploads are disallowed in v1 (XSS); Markdown output is sanitised (nh3).
- Fonts are self-hosted in the output.
