# Section Templates for /docs/

Per-type body templates for concept documents. These are **conventional, not required** — they follow OKF's own stance that "there are no required body sections." Use the template that best matches the concept's `type:`; adapt or drop sections when the concept does not warrant them. The goal is predictable structure for both human readers and agents, not rigid conformity.

## Universal Core

Every concept document benefits from these sections, regardless of type. Use them as the default skeleton when no type-specific template applies.

| Section | Purpose | Guidance |
|---|---|---|
| `# Overview` | 2-3 sentences: what the concept is, who it is for, and the task it addresses | First sentence carries the most important fact; AI systems extract it for summaries |
| `# Prerequisites` | What the reader needs before starting: versions, access, accounts, prior knowledge | Omit only when nothing is required |
| `# Steps` (or `# Behavior`) | The core content: numbered steps, expected outputs, or behavior description | One action per step; flag common errors where they occur |
| `# Examples` | Working code samples, API calls, or config files the reader can copy | Mark placeholders clearly; specify language/runtime per snippet |
| `# Troubleshooting` | Common errors paired with resolutions | Structure each entry as symptom, cause, fix |
| `# References` | Related docs, external standards, or API references | Use root-absolute links (`/docs/...`) |

## Type-Specific Templates

Map each `type:` from `references/okf-conventions.md` to the template that fits best. The section lists are the **minimum conventional skeleton**; add sections when the concept warrants them.

### `Feature` (20-features/)

Sections: `# Overview` → `# Behavior` → `# Options` → `# Examples`

```markdown
---
type: Feature
title: <display name>
description: <one-line summary>
---

# Overview

<2-3 sentences: what the feature does, who uses it, and the problem it solves.>

# Behavior

<How the feature behaves: flows, states, interactions. Cite file:symbol source.>

# Options

<Opt-in flags, env vars, and customization points. One row per option.>

| Option | Default | Description |
|---|---|---|
| <name> | <default> | <what it controls> |

# Examples

<Working usage examples. Mark placeholders clearly.>
```

### `API Reference` (00-core/)

Sections: `# Overview` → `# Endpoint` → `# Parameters` → `# Request / Response` → `# Errors`

```markdown
---
type: API Reference
title: <endpoint or service name>
description: <one-line summary>
---

# Overview

<2-3 sentences: what the endpoint does and who calls it.>

# Endpoint

<Method + path, e.g. `GET /api/v1/orders`.>

# Parameters

<Table of parameters: name, type, required, description.>

# Request / Response

<Example request and response bodies. Mark placeholders clearly.>

# Errors

<Error codes and their meaning.>
```

### `Runbook` (30-operations/)

Sections: `# Trigger` → `# Steps` → `# Verification`

```markdown
---
type: Runbook
title: <incident or procedure name>
description: <one-line summary>
---

# Trigger

<What condition starts this runbook. Cross-link the alert or symptom.>

# Steps

<Numbered steps in order. One action per step.>

# Verification

<How to confirm the runbook succeeded.>
```

### `Deployment` (30-operations/)

Sections: `# Prerequisites` → `# Steps` → `# Rollback`

```markdown
---
type: Deployment
title: <deployment or release name>
description: <one-line summary>
---

# Prerequisites

<Versions, access, and environment state required before deploying.>

# Steps

<Numbered deployment steps.>

# Rollback

<How to revert if the deployment fails.>
```

### `Test Procedure` (30-operations/)

Sections: `# Prerequisites` → `# Steps` → `# Test Inventory`

```markdown
---
type: Test Procedure
title: <test suite name>
description: <one-line summary>
---

# Prerequisites

<Framework version, dependencies, and setup required to run the suite.>

# Steps

<The exact steps to run the suite and to list available tests.>

# Test Inventory

<Available tests or the discovery command that lists them. One line per suite.>
```

### `Schema` (00-core/)

Sections: `# Schema` → `# Joins` → `# Examples`

```markdown
---
type: Schema
title: <table or model name>
description: <one-line summary>
---

# Schema

<Table of columns/fields: name, type, description.>

# Joins

<How this schema relates to others. Use root-absolute links.>

# Examples

<Sample rows or usage.>
```

### `Setup` (00-core/)

Sections: `# Overview` → `# Prerequisites` → `# Setup` → `# Verification`

```markdown
---
type: Setup
title: <setup or environment name>
description: <one-line summary>
---

# Overview

<2-3 sentences: what environment or workflow this sets up and who it is for.>

# Prerequisites

<Versions, accounts, access, or prior knowledge required before starting.>

# Setup

<Numbered steps in order. One action per step.>

# Verification

<How to confirm the setup is complete and correct.>
```

### `Integration` (10-integrations/)

Sections: `# Overview` → `# Setup` → `# Usage` → `# Limitations`

```markdown
---
type: Integration
title: <integration name>
description: <one-line summary>
---

# Overview

<2-3 sentences: what the integration connects and why.>

# Setup

<Credentials, configuration, and environment setup.>

# Usage

<How the integration is used, with examples.>

# Limitations

<Known constraints, rate limits, or unsupported features.>
```

### `Command` (30-operations/)

Sections: `# Overview` → `# Usage` → `# Options` → `# Examples`

```markdown
---
type: Command
title: <command name>
description: <one-line summary>
---

# Overview

<2-3 sentences: what the command does and when to use it.>

# Usage

<The command signature and invocation.>

# Options

<Table of flags and arguments.>

# Examples

<Working invocations.>
```

### `Implementation Plan` (40-plans/)

Sections: `# Scope` → `# Milestones` → `# Rollout`

```markdown
---
type: Implementation Plan
title: <plan name>
description: <one-line summary>
status: proposed
---

# Scope

<What the plan covers and explicitly does not cover.>

# Milestones

<Ordered milestones with acceptance criteria.>

# Rollout

<How the change ships and what happens after.>
```

### `Architecture` (00-core/)

Sections: `# Overview` → `# Components` → `# Data Flow` → `# Constraints`

```markdown
---
type: Architecture
title: <architecture name>
description: <one-line summary>
---

# Overview

<2-3 sentences: the system and its boundaries.>

# Components

<The major components and their responsibilities.>

# Data Flow

<How data moves between components.>

# Constraints

<Non-negotiable constraints and design decisions.>
```

### `Lesson` (99-lessons/)

Sections: `# Context` → `# What Happened` → `# Takeaway`

```markdown
---
type: Lesson
title: <lesson name>
description: <one-line summary>
---

# Context

<The situation that produced the lesson.>

# What Happened

<The event, failure, or dead-end, with source references.>

# Takeaway

<What to do differently next time.>
```

### `Pattern` (25-patterns/)

Sections: `# Overview` → `# When to Use` → `# Pattern` → `# Example`

```markdown
---
type: Pattern
title: <pattern name>
description: <one-line summary>
---

# Overview

<2-3 sentences: the reusable guidance and the problem it solves.>

# When to Use

<The situations or signals that call for this pattern.>

# Pattern

<The steps, rules, or structure to follow. Cite file:symbol source.>

# Example

<An implementation-ready example. Mark placeholders clearly.>
```

## Parsing Template (Doc-First Pass)

When reviewing an existing page, extract these fields to determine whether it matches its type's template. This is the "parse the information" counterpart to the build templates above.

| Field | What to look for |
|---|---|
| `type:` | Does the frontmatter `type:` match the page's actual content? |
| Overview | Is there a 2-3 sentence summary of what the page covers? |
| Core sections | Does the page contain the sections its type's template expects? |
| Source | Does every claim cite a `file:symbol`? |
| Options/params | Are all options, flags, and parameters documented? |
| Examples | Are examples needed, present, working, and clearly marked? |
| Cross-links | Are related concepts linked with root-absolute paths? |
| Status | Is `status:` correct for the type (see `references/okf-conventions.md`)? |

## Adoption Guidance

- **Start minimal.** Use the 2-5 section skeleton per type. Add sections only when a recurring gap appears.
- **Keep sections conventional, not required.** A concept that does not warrant a section should omit it, matching OKF's "no required body sections" rule.