# ADR 008: Blog posts are Markdown, edited with a toolbar and a live real preview

Status: accepted (WYSIWYG rich text deferred)

## Decision
- Posts are stored as Markdown (`posts.body_md`), rendered at build time with markdown-it-py with
  raw HTML disabled and the output sanitised again with nh3. Images are referenced as
  `asset:<id>` and resolved by the builder to the exported file (or the media URL in preview).
- The editor is a Markdown textarea with a formatting toolbar (bold, italic, headings, lists,
  quote, link, image from the library). The adjacent preview is the *real* generated page (ADR 001),
  so what the author sees is exactly what is published.
- Each translation is its own post sharing a `translation_group` (ADR 006).

## Why not a WYSIWYG editor (Tiptap) now
Round-tripping rich text <-> Markdown with custom `asset:` images is the risky part, and the
live preview already gives non-technical users what they need. A Tiptap editor can replace the
textarea later without any change to storage, the builder or the API.

## Consequences
Authors see Markdown syntax in the text box (the toolbar means they rarely type it). Revisit if
clients find it intimidating.
