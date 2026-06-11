# Project Instructions — Economic Policy Simulator

You are working on the ITCILO Economic Policy Simulator (FastAPI backend, React/Vite frontend, deployed on Render). Its sole purpose is DIDACTIC: learners (many of them policy makers) explore the direction, transmission channels and rough magnitude of employment effects of policy choices. It is NOT a forecasting or decision-support tool.

## Non-negotiable ground rules

1. No invented numbers. Every coefficient must be computed from a real dataset by reproducible code, or carry a full citation in the assumptions registry (backend/app/data/assumptions.json). It is forbidden to type numeric matrices, multipliers, elasticities or shares directly into source code.
2. No false provenance. Never label values "OECD", "TiVA", "research-grade" or similar unless they were programmatically derived from the named dataset by code in this repository.
3. The model core is a demand-driven Leontief input-output model computed from the OECD ICIO 2025 edition tables, with employment from OECD Trade in Employment (TiM) and ILOSTAT. All behavioural extensions (elasticities, induced effects) must be explicit, sourced and toggleable.
4. Acceptance constraint: under default parameters, a unilateral tariff increase must NOT produce a net positive aggregate employment effect (consistent with Flaaen and Pierce 2019; Amiti, Redding and Weinstein 2019). An automated test enforces this.
5. If required data is missing, stop and report; never substitute a guessed value.
6. Deployment discipline: commit freely, but push to main (which auto-deploys) ONLY after `pytest` passes locally. The GitHub Action (`.github/workflows/tests.yml`) re-runs the suite, the API-contract smoke and the frontend build on every push; a red Action on main must be fixed immediately.
7. Secrets only via environment variables. No em-dashes in user-facing text; use en-dashes with spaces.
8. Maintain CHANGELOG.md and project_context.md as before (rules below).

## Deployment
- Auto-deploy is active: `git push origin main` triggers Render.com rebuild.
- Push only after `pytest` passes locally (ground rule 6); CI re-runs the suite on GitHub.
- Classroom delivery: paid Render instance or /health keep-alive ping (see DEPLOYMENT.md).

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
Current version: **1.0.0** (2026-06-11)
The post-audit overhaul (Phases 1-4) is complete. No next session planned; maintenance mode.
