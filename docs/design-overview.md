# GizmoApp Design Overview

This document records the design intent behind the scaffold so future edits can
extend it without rediscovering core assumptions.

## Purpose

GizmoApp is a starter repository for building small public web apps that can be
edited incrementally by Codex. The initial state is intentionally blank, but the
shape of the project is meant to support:

- touch-friendly interaction on phones and tablets
- desktop browser support
- either a graphical shell or a text-first shell
- low-friction deployment on a single Linux host
- simple operational behavior that a non-expert user can follow

## Core Constraints

- Keep the frontend build-free unless the user explicitly chooses otherwise.
- Keep deployment centered on one host with `nginx`, `gunicorn`, and SQLite.
- Keep the app prefix-aware so it can live at `/<repo-name>/` instead of only `/`.
- Keep the code understandable enough that a future Codex session can work from
  the repository alone.

## High-Level Architecture

The app has three main layers:

1. Flask backend
   - Serves HTML, JSON API routes, health/admin endpoints, and static assets.
2. SQLite persistence
   - Stores a small sample schema and seed data for future feature work.
3. Shell-specific frontend
   - `graphical` shell for canvas-heavy or game-like interaction.
   - `text` shell for forms, dashboards, and conventional application flows.

Both shells share the same backend, deployment process, and database.

## Shell Model

Shell selection is a deployment/runtime choice, not a repo split.

- `server/wsgi.py` serves whichever shell is active.
- `server/wsgi_graphical.py` forces the graphical shell.
- `server/wsgi_text.py` forces the text shell.

The intended default for template-derived apps is to store the chosen shell in
`deploy/app.env`, commit it, and push it. The deploy pipeline then applies that
setting to the live service without requiring a manual SSH edit on the server.

## Routing And Prefix Design

The scaffold is designed to run at either:

- `/`
- or a path prefix such as `/<repo-name>/`

That is why the backend, manifest, static asset URLs, and API routes all use a
configurable `GIZMOAPP_URL_PREFIX`.

This is important because the deployment model assumes multiple independent apps
can share one host under different path prefixes.

## Configuration Model

There are two different configuration layers by design.

### Git-tracked deployment settings

`deploy/app.env` is for non-secret settings that should reach the server through
normal Git pushes and cron-driven deploys. Today that mainly means:

- `GIZMOAPP_SHELL`

### Live machine-specific settings

`.env` is for settings that should stay local to one deployed checkout:

- `GIZMOAPP_SECRET_KEY`
- `GIZMOAPP_PORT`
- `GIZMOAPP_DB_PATH`
- `GIZMOAPP_SYSTEMD_USER_SERVICE`
- `GIZMOAPP_URL_PREFIX`

For local development, the app reads `deploy/app.env` and then `.env`.

For deployed services, systemd loads `.env` directly into the process
environment. The deploy scripts keep selected git-tracked keys synchronized from
`deploy/app.env` into `.env`.

## Deployment Model

The intended production shape is:

- one Linux host
- `nginx` as the public entry point
- one user-level `gunicorn` service per app instance
- one app checkout at `/home/kevinlb/bin/<name>`
- one once-per-minute cron entry per app instance

The deployment flow is intentionally split:

1. one-time machine bootstrap
2. per-instance install
3. git push for later updates

This keeps the install model understandable while still allowing many derived
apps to coexist on one server.

## Nginx Layout

Path-based routing should live in a neutral host config, not in an app-named
site file.

Preferred shape:

- one host file such as `/etc/nginx/sites-enabled/vickrey10`
- one snippet per app in `/etc/nginx/gizmoapp-instances/<name>.conf`

That allows future app installs to register themselves without hand-editing the
main host config every time.

## Update And Reload Semantics

The deploy process is intentionally selective:

- static asset changes usually do not require a gunicorn reload
- Python or template changes do require the service to reload or restart
- `deploy/app.env` changes require a restart so the new environment takes effect

Cron-driven deploys that call `systemctl --user` need the user systemd bus
environment. The scaffold therefore treats `XDG_RUNTIME_DIR` and
`DBUS_SESSION_BUS_ADDRESS` as part of the deployment design, not an incidental
detail.

## Operational Boundaries

The scaffold is optimized for:

- one host
- modest traffic
- anonymous/public access
- incremental feature development

It is not currently optimized for:

- multi-host orchestration
- background job queues
- offline-first behavior
- secret management beyond per-checkout `.env`
- high-write database workloads

## Extension Guidance

When extending the project:

- prefer shared backend changes when both shells need the feature
- keep shell-specific UI isolated under the shell’s own template/static files
- avoid introducing hidden build steps unless they are clearly worth the added
  operational cost
- preserve prefix-aware routing and multi-app deployment assumptions

If a future change breaks any of those assumptions, update this document,
`README.md`, and `AGENTS.md` together.
