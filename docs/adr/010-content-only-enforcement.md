# ADR 010: The client's content-only role is enforced by whitelist merge

Status: accepted (implements ADR 005)

## Decision
An `editor` may `PUT` the site document, but the server first builds an *expected* document:
the stored document with only whitelisted content fields copied over from the submission
(content-group props of existing sections, list items, business info, tagline/footer text/default
description, translations, page SEO texts). If the expected document differs from the submission,
the save is rejected with 403 and the list of offending paths. Nothing is saved.

## Why a whitelist, not a blacklist
Anything not explicitly allowed is locked, including fields added to the schema later and keys a
hand-crafted request invents. The editor UI hides the same controls, but only the server decides.

## Consequences
Content fields are defined once, by the `group: content` tag on each prop (also what drives
translation and the properties panel). 47 unit cases and API tests pin down what is and is not
allowed; add a case whenever a new top-level field appears.
