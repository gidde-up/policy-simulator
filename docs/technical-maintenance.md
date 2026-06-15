# Technical maintenance notes

Operational notes that do not belong in the methodology or the changelog.
Last reviewed: 2026-06-15 (v1.2.0).

## Dormant endpoints (chat / explain / suggest)

The backend still defines `POST /api/chat`, `POST /api/explain` and
`GET /api/suggest/{iso3}`, and the frontend keeps `ChatPanel.jsx` and the
corresponding `services/api.js` wrappers. **None of these are mounted in
the UI** (`App.jsx` does not render `ChatPanel`, and no component calls the
wrappers). They are retained as disabled/internal scaffolding from an
earlier design, not part of the supported didactic surface.

Status: **disabled/internal.** They are not advertised, not linked, and not
covered by the contract smoke. If they are ever re-enabled they must not
generate free-text model interpretations that bypass the methodology and
assumptions registry (the whole tool is built on traceable, sourced
numbers). Preferred future action: delete them, or gate them behind an
explicit feature flag with tests asserting they only return
registry-backed content.

## Frontend dependency audit (npm audit)

As of 2026-06-15, `npm audit` reports 7 advisories (1 low, 1 moderate,
5 high), all in **build-time tooling**:

- `rollup` (via `vite`) - path traversal in the bundler;
- `postcss` (via `tailwindcss`/build) - XSS in CSS stringify output.

These affect the build/dev toolchain, not the deployed artefact: the
production output is a static SPA (HTML/CSS/JS) with no server-side
rendering and no runtime use of rollup or postcss. The advisories are not
reachable by an end user of the deployed site.

Decision: **not patched in v1.2.0.** `npm audit fix --force` would pull a
new Vite major and risk the build close to a release. Revisit on the next
dependency-maintenance pass: run `npm audit fix` (non-breaking first),
then a deliberate Vite/Rollup major upgrade with a full build + manual
smoke. Re-run `npm audit` and update this note when done.
