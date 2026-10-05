# ADR 009: Every export is a stored, versioned artifact

Status: accepted

## Decision
`POST /projects/{id}/exports` builds the saved site, stores the ZIP in object storage, and records
`exports(doc_revision, size, file_count, issues, created_by)`. Downloads are authenticated,
per project, and the last 10 per project are kept (artifacts are deleted with the rows).
The dialog shows build warnings before the user downloads.

## Why
- The same artifact is what automatic publishing will deploy later (ADR 004): publish becomes
  "upload export N to a host", with rollback for free.
- Reproducibility: an old export is byte-for-byte what was delivered, regardless of later
  generator changes.
- No lock-in is visible: `export.json` + `posts.json` inside the ZIP are the re-importable source.

## Consequences
Storage grows with exports (bounded by retention). Exports are built synchronously in the
request (fast for small sites); move to a background job when sites get large.
