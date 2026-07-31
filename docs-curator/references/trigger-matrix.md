# Trigger Matrix

Maps changed files to the doc sections that need attention. Use it as a starting point, not as an exhaustive rule. A change can span multiple rows; classify once, then walk every row that matched.

| Change | Update | Why |
|---|---|---|
| Endpoint added, changed, or removed | `/docs/00-core/` API docs + related feature and integration docs | Public contract changed |
| Migration, model, or index change | `/docs/00-core/` schema and architecture docs + impacted feature docs | Data shape changed |
| Integration behavior change | `/docs/10-integrations/` + dependent `/docs/20-features/` docs | External surface changed |
| Event, listener, or job change | `/docs/20-features/` workflow docs + `/docs/00-core/` architecture | Async flow changed |
| Command or schedule change | `/docs/30-operations/` console commands | Operational surface changed |
| Deployment procedure change | `/docs/30-operations/` deployment | Runtime assumptions changed |
| Setup or env variable change | `/docs/00-core/` setup + `/docs/index.md` + `README.md` docs section | Onboarding path changed |
| Scope, milestone, or rollout assumption changed | Related `/docs/40-plans/` file(s) + corresponding `/docs/` pages | Plan no longer matches reality |
| New `.env.example` entries | `docs/00-core/setup` and the integration or feature page that consumes the var | Docs and example must agree |
| `mkdocs.yml`, `docs/index.md`, or nav reorg | All `/docs/` pages touched by the move | Link integrity |
| Plan shipped | **Delete** the plan file under `/docs/40-plans/`, update `/docs/40-plans/index.md` and `/docs/index.md`, fix any cross-references | Plans are delete-on-ship; see `references/okf-conventions.md` |
| Plan abandoned | Move to `/docs/99-lessons/` with `type: Lesson` and a brief retrospective | Preserve the learning |

## Classification Heuristics

When classifying, prefer signal from these patterns:

- `**/routes/**`, `**/controllers/**`, `**/api/**` -> Endpoint
- `**/migrations/**`, `**/models/**`, `**/schema/**`, `**/factories/**` -> Migration or model
- `**/integrations/**`, `**/services/**` (third-party) -> Integration
- `**/events/**`, `**/listeners/**`, `**/jobs/**`, `**/queues/**` -> Event or job
- `**/console/**`, `**/commands/**`, `**/Kernel.php`, `**/scheduler/**` -> Command or schedule
- `**/deploy/**`, `**/Dockerfile*`, `**/k8s/**`, `**/terraform/**`, `.github/workflows/**` -> Deployment
- `.env*`, `**/config/**` -> Setup or env

When in doubt, classify as the most user-visible category and let the report do the rest.
