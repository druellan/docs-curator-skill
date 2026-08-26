# OKF Conventions for /docs/

This directory is an OKF v0.1 knowledge bundle. See [the spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for the full conformance rules. This document pins down the project-specific choices.

## Conformance

Per OKF v0.1 §9, a bundle is conformant when:

1. Every non-reserved `.md` file in the tree contains parseable YAML frontmatter.
2. Every frontmatter block contains a non-empty `type:` field.
3. Reserved filenames (`index.md`, `log.md`) follow the structure described in OKF §6 and §7 when present.

Reserved filenames MUST NOT be used for concept documents.

## Type Vocabulary

The project uses a controlled type vocabulary so consumers can filter, route, and visualize. Use the type from this table that best matches the concept. If nothing fits, propose a new type and add it here.

| Type | Used in | Purpose |
|---|---|---|
| `Architecture` | `00-core/` | High-level system architecture or design overview |
| `API Reference` | `00-core/` | API endpoint, route, or service interface |
| `Schema` | `00-core/` | Data model, table, migration, or index |
| `Setup` | `00-core/` | Onboarding, environment setup, or local development |
| `Integration` | `10-integrations/` | Third-party service, vendor, or external system |
| `Feature` | `20-features/` | Product feature, user-facing capability, or workflow |
| `Runbook` | `30-operations/` | Incident response or on-call procedure |
| `Test Procedure` | `30-operations/` | Commands and procedures for running the project's test suite, including how to list available tests |
| `Deployment` | `30-operations/` | Deployment procedure, release flow, or infrastructure |
| `Command` | `30-operations/` | CLI command, scheduled task, or console entry point |
| `Implementation Plan` | `40-plans/` | WIP implementation plan (see lifecycle below) |
| `Lesson` | `99-lessons/` | Post-mortem, retrospective, or verified-dead-end finding (see trigger matrix) |

## Frontmatter

Minimum required frontmatter:

```yaml
---
type: <one of the types above>
title: <human-readable display name>
description: <one-line summary>
---
```

Recommended fields (in priority order):

- `title` — human-readable display name. If omitted, consumers may derive from filename.
- `description` — one sentence; used in `index.md` and search snippets.
- `resource` — URI for the underlying asset, if any.
- `tags` — list of short strings for cross-cutting categorization.
- `timestamp` — ISO 8601 datetime of last meaningful change.
- `status` — concept lifecycle state. Allowed values depend on type (see below).

Producers MAY add any other keys. Consumers MUST NOT reject unknown keys.

## Status by Type

| Type | Allowed `status` values | Default |
|---|---|---|
| `Architecture` | (none) | — |
| `API Reference` | `draft`, `stable`, `deprecated` | `stable` |
| `Schema` | `draft`, `stable`, `deprecated` | `stable` |
| `Integration` | `draft`, `stable`, `deprecated` | `stable` |
| `Feature` | `draft`, `stable`, `deprecated` | `stable` |
| `Runbook` | `draft`, `stable`, `deprecated` | `stable` |
| `Test Procedure` | `draft`, `stable`, `deprecated` | `stable` |
| `Deployment` | `draft`, `stable`, `deprecated` | `stable` |
| `Command` | `draft`, `stable`, `deprecated` | `stable` |
| `Implementation Plan` | `proposed`, `accepted`, `delayed` | `proposed` |
| `Lesson` | (none) | — |

## Implementation Plan Lifecycle

Plans in `/docs/40-plans/` follow an aggressive delete-on-ship lifecycle. The reasoning: once a feature ships, the "why" lives in the shipped code, the architecture, and the lessons archive. Stale plans add noise without adding context.

1. **Create** with `status: proposed` and a clear scope, milestones, and rollout.
2. **Accept** by changing `status: accepted` when implementation starts.
3. **Ship**: when the feature is in production, **delete the plan file** and:
   - Remove the entry from `/docs/40-plans/index.md` (if present).
   - Remove any link from `/docs/index.md`.
   - Update any cross-references in feature or integration docs to point at the shipped feature doc instead.
   - Add a one-line `## Provenance` note in the shipped feature doc if the rationale deserves a permanent home.

A plan that is abandoned before shipping should be moved to `/docs/99-lessons/` with `type: Lesson` and a brief retrospective.

## Cross-Links

- Use root-absolute paths, ex: `/docs/10-integrations/stripe.md`.
- Do not use relative paths; root-absolute paths are stable when documents move.
- Links express directed relationships; the surrounding prose conveys the relationship type.
- Consumers MUST tolerate broken links.

## Reserved Filenames

- `index.md` — directory listing for progressive disclosure. No frontmatter (per OKF §6), except the bundle root which MAY declare `okf_version`.
- `log.md` — chronological change history for the directory. Newest first, ISO 8601 date headings.

All other `.md` files in the tree are concept documents and MUST have frontmatter.
