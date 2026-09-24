# OKF conventions for /docs/

This directory is an OKF v0.2 knowledge bundle. See [the spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for the full conformance rules. This document pins down the project-specific choices.

## Conformance

Per OKF v0.2 §11, a bundle is conformant when:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure described in §8 and §9 when present.

`scripts/check-integrity.py` validates all three items. It enforces the project fields above (`title`, `description`, `generated`, `okf_version`, and the `status` vocabulary) by default; pass `--lenient` to check OKF conformance only. The same tool checks index coverage and description sync.

Consumers MUST NOT reject a bundle because of a missing optional field, an unknown `type` value, an unknown extra key, a broken cross-link, or a missing `index.md`. Conformance is minimal on purpose; the vocabulary and rules below are project conventions layered on top.

## Type vocabulary

The project uses a fixed type vocabulary so consumers can filter, route, and visualize. Every concept must use a type from this table. Choose the type that best describes the page's primary purpose; do not add new types.

| Type | Used in | Purpose |
|---|---|---|
| `Architecture` | `00-core/` | High-level system architecture or design overview |
| `API Reference` | `00-core/` | API endpoint, route, or service interface |
| `Schema` | `00-core/` | Data model, table, migration, or index |
| `Setup` | `00-core/` | Onboarding, environment setup, or local development |
| `Integration` | `10-integrations/` | Third-party service, vendor, or external system |
| `Feature` | `20-features/` | Product feature, user-facing capability, or workflow |
| `Pattern` | `25-patterns/` | Reusable guidance, playbook, or convention that applies across multiple features |
| `Runbook` | `30-operations/` | Incident response or on-call procedure |
| `Test Procedure` | `30-operations/` | Commands and procedures for running the project's test suite, including how to list available tests |
| `Deployment` | `30-operations/` | Deployment procedure, release flow, or infrastructure |
| `Command` | `30-operations/` | CLI command, scheduled task, or console entry point |
| `Implementation Plan` | `40-plans/` | WIP implementation plan (see lifecycle below) |
| `Lesson` | `99-lessons/` | Post-mortem, retrospective, or verified-dead-end finding (see trigger matrix) |

OKF does not prescribe a type list and requires consumers to tolerate unknown values. This project's fixed vocabulary is a rule for pages the skill writes, not an additional OKF conformance requirement.

## Frontmatter

Required by OKF (§4.1):

```yaml
---
type: <one of the types above>
---
```

Required by this project on top of OKF:

```yaml
---
type: <one of the types above>
title: <human-readable display name>
description: <one-line summary>
generated: { by: docs-curator/<version>, at: <ISO 8601 datetime> }
---
```

`description` is not decoration: it feeds the page's entry in `index.md` and search snippets.

Recommended fields, in priority order:

- `status`: lifecycle state (§5.4). See the per-type table below.
- `tags`: list of short strings for cross-cutting categorization.
- `resource`: URI for the underlying asset, if any.
- `sources`: the material the page derives from (§5.1). Use it instead of a body citations list.
- `verified`: who or what confirmed the page against its sources (§5.2).
- `stale_after`: absolute instant after which the page is stale (§5.5).

Producers MAY add any other keys. Consumers MUST NOT reject unknown keys.

### Actor convention

`generated.by` and `verified[].by` record an identity in one of three forms (§7):

- `<producer>/<version>` for agents and tools, using the skill name and its installed version.
- `human:<id>` for a person, for example `human:dario`.
- `process:<id>` for an automated process, for example `process:release-please`.

Consumers classify trust by the `human:` prefix, so use it on content that a person wrote or confirmed.

### generated

```yaml
generated: { by: docs-curator/<version>, at: <ISO 8601 datetime> }
```

Both keys are required when `generated` is present. `at` is an ISO 8601 datetime with a UTC offset. Write `generated` on every page created, and bump `at` on every page edited. This field supersedes the v0.1 `timestamp`; consumers MAY fall back to `timestamp` on legacy pages.

### verified and trust tiers

```yaml
verified: { by: human:dario, at: 2026-09-16T00:00:00Z }
```

`verified` lists the checks that confirmed the content, independent of who wrote it. A bare mapping is a one-element list. Consumers derive a trust tier from it (§5.3): no key means unverified, non-`human:` actors only means machine-confirmed, and a `human:<id>` entry means human-reviewed. Set it when a person or a deterministic process confirmed the page against its sources.

### sources and per-claim attribution

```yaml
sources:
  - id: orders-schema
    resource: https://example.com/orders-schema
    title: Orders export schema
    author: team:backend
    last_modified: 2026-08-30T00:00:00Z
usage_window: { from: 2026-09-01T00:00:00Z, to: 2026-09-30T00:00:00Z }
```

`sources[].resource` is required in each entry. The credibility signals `author`, `usage_count`, and `last_modified` are optional; pair `usage_count` with the `usage_window` sibling. Attribute one claim with a footnote whose label is the source `id`:

```markdown
The `events` table is sharded daily.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

Footnote labels are keys, not positions, so they survive a reordered list.

### status and stale_after

`status` is `draft`, `stable`, or `deprecated` (§5.4). Absent means `stable`.

`stale_after` is an absolute instant, not a TTL (§5.5). Set it on pages whose facts decay: test procedure inventories, integration limitation lists, and lesson findings tied to a vendor release. A consumer compares `now >= stale_after` with no reference to when the page was read.

## Status by type

| Type | Allowed `status` | Default |
|---|---|---|
| All types | `draft`, `stable`, `deprecated` | `stable` |
| `Implementation Plan` | `draft`, `stable`, `deprecated` | `draft` |

## Implementation plan lifecycle

Plans in `/docs/40-plans/` follow an aggressive delete-on-ship lifecycle. The reasoning: once a feature ships, the "why" lives in the shipped code, the architecture, and the lessons archive. Stale plans add noise without adding context.

1. **Create** with `status: draft` and a clear scope, milestones, and rollout.
2. **Accept** by changing to `status: stable` when implementation starts.
3. **Ship**: when the feature is in production, **delete the plan file** and:
   - Remove the entry from `/docs/40-plans/index.md` (if present).
   - Remove any link from `/docs/index.md`.
   - Update any cross-references in feature or integration docs to point at the shipped feature doc instead.
   - Add a one-line `## Provenance` note in the shipped feature doc if the rationale deserves a permanent home.

If the user explicitly requests a lesson about a plan abandoned before shipping, move it to `/docs/99-lessons/` with `type: Lesson` and a brief retrospective. Otherwise, report the abandoned plan and ask what to preserve before removing it. A plan that is deferred stays `draft`. Do not invent a separate status value; consumers filter on the three lifecycle values above.

## Cross-links

- Use root-absolute paths, ex: `/docs/10-integrations/stripe.md`.
- Do not use relative paths; root-absolute paths are stable when documents move. OKF also permits relative links (§6.1), but this project standardizes on root-absolute and `scripts/check-integrity.py` enforces it.
- Links express directed relationships; the surrounding prose conveys the relationship type.
- Consumers MUST tolerate broken links.

## Index files

`index.md` appears in any directory, including the bundle root, and lists that directory's contents for progressive disclosure (§8). It carries no frontmatter, with one exception: the bundle-root `/docs/index.md` declares the version it targets:

```markdown
---
okf_version: "0.2"
---

# Core

- [Architecture](/docs/00-core/architecture.md) - How the service fits together
- [Setup](/docs/00-core/setup.md) - Local environment and environment variables

# Features

- [Orders](/docs/20-features/orders.md) - Create, edit, and cancel orders
```

Rules:

- Every entry is a link plus the linked page's `description`.
- Add a page to the index in the same pass that creates it, and keep the entry's description in sync when the page changes.
- Group entries under headings. Use one section per type or per directory, whichever reads better, and stay consistent within the bundle.
- List a subdirectory as a link to its `index.md`.

## Log files

`log.md` records the history of its directory when the bundle keeps one (§9). It is optional, but when present it is append-only, newest first, with ISO 8601 `YYYY-MM-DD` date headings:

```markdown
# Directory update log

## 2026-09-16

- **Update**: Added the retry policy to [Orders](/docs/20-features/orders.md).

## 2026-09-10

- **Creation**: Created the [Setup](/docs/00-core/setup.md) page.
```

The leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is a convention, not a requirement.

## Reserved filenames

`index.md` and `log.md` are reserved at every level and MUST NOT be used for concept documents (§3.1). All other `.md` files in the tree are concept documents and carry frontmatter.
