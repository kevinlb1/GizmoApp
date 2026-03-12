# GizmoApp

GizmoApp is a blank webapp template repository intended to be easy for later Codex edits. It ships with:

- A Python `Flask` backend that serves both the app shell and JSON API
- A lightweight SQLite data store with a sample table and seed rows
- A touch-friendly graphical shell with a canvas-driven scene
- A more standard text-first application shell
- Deployment examples for `nginx` in front of `gunicorn`
- A cron-friendly deploy script that fast-forwards from `main` and reloads `gunicorn` only when runtime changes require it

## Why No Frontend Build Step

The initial scaffold intentionally avoids Node and a frontend bundler. That keeps deployment and future edits simpler while still leaving room for richer rendering later. The frontend is split into small modules, and the canvas renderer is isolated so a future change can swap in PixiJS, Three.js, or another engine without restructuring the backend.

## Repository Layout

- `server/` contains the Flask app, SQLite wiring, and HTML/CSS/JS assets
- `scripts/` contains install, deploy, and asset-generation helpers
- `deploy/` contains example `gunicorn`, `nginx`, and cron snippets
- `tests/` contains API and routing smoke tests

## Local Development

1. Copy `.env.example` to `.env` if you want to test a non-root URL prefix such as `/AI100`.
2. Create the virtualenv and install dependencies:

```bash
make install
```

3. Initialize the SQLite database:

```bash
make init-db
```

4. Run the development server:

```bash
make dev
```

Or start a specific shell explicitly:

```bash
make dev-graphical
make dev-text
```

The default app URL is `http://127.0.0.1:8001/` unless you set `GIZMOAPP_URL_PREFIX`, in which case the app lives under that prefix.

## Shell Selection

The project keeps both blank shells in the same codebase and shares the same backend, API, database, and deployment scripts.

- `server/wsgi_graphical.py` serves the graphical shell
- `server/wsgi_text.py` serves the text-first shell
- `server/wsgi.py` serves whichever shell is selected by `GIZMOAPP_SHELL`

On the server, the simplest approach is to keep the gunicorn target at `server.wsgi:app` and set `GIZMOAPP_SHELL=graphical` or `GIZMOAPP_SHELL=text` in `.env`.

## Using This As A Starter

If you want future users to create their own apps from this starting point, GitHub template repositories are usually a better fit than forks.

- Use a template repository when the new project should start with the same files but become its own independent app and history.
- Use a fork when the main goal is to contribute changes back to this repository while preserving GitHub’s fork relationship.

For this repository, the intended use is as a starter/template. A derived app should usually get its own repo name, its own deployment target, and its own branding rather than staying tied to GizmoApp.

To support that use case, keep these traits intact:

- configuration lives in `.env`
- deployment steps stay explicit in `README.md` and `deploy/`
- the backend remains shared and understandable
- shell-specific UI stays isolated so future projects can keep one shell or both

## API Surface

- `GET /api/bootstrap` returns app metadata, health details, and the seeded sample nodes
- `GET /api/sample-nodes` lists the sample rows from SQLite
- `POST /api/sample-nodes` inserts a sample row for future experimentation
- `GET /healthz` returns a simple JSON health response
- `GET /admin/` shows a small admin summary page

If `GIZMOAPP_URL_PREFIX` is set, all of those routes live under the prefix. For example, `/AI100/api/bootstrap`.

## Deployment Notes

### Manual server install

Run this once on the server after the repository is cloned:

```bash
./scripts/install_server.sh
```

The script installs system packages, creates `.venv`, installs Python dependencies, initializes the SQLite database, and respects the selected `GIZMOAPP_SHELL` from `.env`.

### `gunicorn` reload behavior

Static asset changes do not require a `gunicorn` reload because Flask serves them from disk on each request. Backend Python and template changes do require a reload so workers pick up the new code. The deploy script detects that difference and only attempts a reload when needed.

### Cron deployment

The example cron entry in `deploy/user-crontab.example` calls `scripts/deploy_from_git.sh` once per minute. That script:

- Refuses to deploy if tracked files are dirty
- Fast-forwards the live checkout from `origin/main`
- Reinstalls Python packages only when `server/requirements.txt` changes
- Re-initializes the database idempotently
- Reloads `gunicorn` when runtime files changed and a reload strategy is configured

### HTTPS and installability

Reliable PWA installation on iPhone and Chromium-based browsers requires HTTPS. If `vickrey10.cs.ubc.ca` is only available over plain HTTP, the app will still run in the browser, but install prompts and standalone behavior will be limited or unavailable.
