# ADR 004: ZIP export first; publishing later

Status: accepted

## Decision
v1 produces a ZIP (plain HTML/CSS/assets/fonts, README, `export.json`). The ZIP must work from `file://` (relative URLs). No background worker or hosting integration in v1.
A one-method `Deployer` interface may exist with a single `ZipExport` implementation so later targets are additive.

## Post-v1 plan
Cloudflare Pages Direct Upload (or Workers Static Assets, verify which is current) with a bring-your-own API token, via a DB-backed worker. Then custom domains. Managed multi-tenant hosting (Worker + R2 by hostname) only if needed.

## Consequences
Removes the largest external dependency, the job runner and encrypted token storage from v1. Publish is a manual upload for now; this teaches what automatic publishing needs.
