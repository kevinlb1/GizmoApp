# Agent Extension Guide

This repo is meant to answer common setup questions before a future coding agent
has to ask them.

## Default Stack

- Backend: Flask in `server/gizmoapp_server/`
- Persistence: SQLite through `server/gizmoapp_server/db.py`
- Text UI: `server/gizmoapp_server/templates/index_text.html` and `static/app/text/`
- Graphical UI: `server/gizmoapp_server/templates/index.html` and `static/app/`
- Shared styling: `server/gizmoapp_server/static/app/base.css`
- Optional frontend helpers: `server/gizmoapp_server/static/app/capabilities/`
- Optional backend helpers: `server/gizmoapp_server/capabilities/`

Keep new work prefix-aware by building routes with `scoped_path` and reading API
URLs from the injected browser config instead of hard-coding `/api`.

## Persistence

Use SQLite first. Add schema changes as migrations in `SCHEMA_MIGRATIONS` inside
`server/gizmoapp_server/db.py`. Keep local data under `var/`, which is ignored by
Git.

For general app state, prefer `app_state`. For append-only user-visible activity,
prefer `app_events`. Add domain tables only when the feature has real domain
data.

## UI

Use the shared app frame and tokens in `base.css` before inventing new layout
chrome. Keep cards at 8px radius. Keep text compact enough for phone, tablet,
laptop, and desktop widths.

Choose the text shell for forms, lists, dashboards, records, and workflows.
Choose the graphical shell for canvas, animation, map-like views, sprites,
games, simulations, and rich visuals.

## Graphics

The graphical shell is not limited to polygons and ellipses. `SceneRenderer`
supports:

- generated bitmap textures
- loaded image textures
- layered sprites with opacity and rotation
- database-backed visual nodes
- pointer-driven animation

For heavier visuals, add a renderer adapter under `static/app/` and lazy-load
the library only from the shell that needs it.

## Audio

Use `static/app/capabilities/audio.js` for browser microphone capture. Send
sample arrays to `POST /api/audio/analyze` for dependency-free analysis. Add
heavier audio libraries only when the user asks for transcription, classification,
or signal processing that needs them.

## Search

Start with `GET /api/search?q=...` and SQLite queries. If a feature needs richer
local search, add SQLite FTS tables in a migration before introducing an external
search service.

## Optimization

Start with `POST /api/optimize/route` and pure-Python algorithms. Bring in a
specialized solver only when the requested optimization problem outgrows that
simple path.

## Mapping And Location

Use OpenStreetMap by default. `GET /api/map/default` returns the tile URL template,
attribution, and default location.

For location-dependent features, assume the user is at UBC Vancouver unless they
give a different location.

## Machine Learning

Use scikit-learn when the user requests ML. Keep it optional:

```bash
.venv/bin/pip install -r server/requirements-ml.txt
```

Do not add scikit-learn to `server/requirements.txt` unless ML becomes mandatory
for the base template.
