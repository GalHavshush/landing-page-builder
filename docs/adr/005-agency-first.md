# ADR 005: Agency mode first

Status: accepted

## Decision
The first user is the author building client sites. Roles (owner, designer, editor), invite links (no email infra) and a content-only client editor come right after the core editor (M19).
Prop fields are tagged `group: content | design`. Servers enforce it: on save, an editor's change set is diffed against the stored document and rejected if it touches design props or structure. Hiding controls in the UI is not security.
Shared business info (hours, phone, address, socials) lives in `site.business` and is read by sections, so clients edit it once.
