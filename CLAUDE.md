# Project Instructions — Economic Policy Simulator

## Deployment
- Auto-deploy is active: `git push origin main` triggers Render.com rebuild.
- After any commit that changes functionality, push immediately — do not ask for confirmation.

## CHANGELOG.md — mandatory maintenance
- **Update CHANGELOG.md at the end of every session** before committing and pushing.
- Add a new version entry at the top of the file under the current version heading, or create a new version heading if the changes warrant a minor bump (see rules below).
- Entry format: version number, date, session number if known, bullet list of changes grouped by Backend / Frontend / Bug fixes.
- Keep entries factual and concise — use source-level language, not marketing language.

### Versioning rules
| Change type | Bump |
|-------------|------|
| New country, new policy lever, new output metric, new major UI section | MINOR (0.x.0) |
| Bug fix, label change, UI refinement, documentation update, parameter recalibration | PATCH (0.x.y) |
| Breaking API change or full model replacement | MAJOR (x.0.0) — confirm with user |

### Version string
- Keep `__version__` in `backend/app/main.py` in sync with the latest CHANGELOG entry.

## project_context.md — mandatory maintenance
- **Update project_context.md at the end of every session** to reflect any changes to: project structure, key files, API endpoints, data sources, model parameters, environment setup, or known issues.
- Do NOT add session history here — that belongs in CHANGELOG.md.
- Keep the technical reference accurate and current; it is the primary onboarding document for resuming work.

## Project version
Current version: **0.9.0** (2026-03-16)
Next planned: **0.10.0** — Learner/Didactic fixes continued (guided mode, scenario compare, policy lever anchoring)
