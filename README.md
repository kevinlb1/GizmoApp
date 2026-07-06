# GizmoApp

GizmoApp is a blank webapp template repository intended to be easy for later Codex edits. It ships with:

- A Python `Flask` backend that serves both the app shell and JSON API
- A lightweight SQLite data store with migrations and app state tables
- A touch-friendly graphical shell with sprite/bitmap-first rendering and layered texture support
- A minimal text-first shell with the same responsive app frame
- No public starter chrome: Admin remains available by direct route, but blank public shells show no Admin/Install/status controls
- Lazy capability APIs for audio analysis, search, optimization, mapping, and optional machine learning
- Deployment examples for `nginx` in front of `gunicorn`
- A cron-friendly deploy script that fast-forwards from `main` and reloads `gunicorn` only when runtime changes require it

## Why No Frontend Build Step

The scaffold intentionally avoids Node and a frontend bundler. That keeps deployment and future edits simpler while still leaving room for richer rendering later. The frontend is split into small modules, and the canvas renderer defaults to generated bitmap sprites so a future change can add sprite sheets, PixiJS, Three.js, map tiles, or generated image assets without restructuring the backend.

## Repository Layout

- `server/` contains the Flask app, SQLite wiring, and HTML/CSS/JS assets
- `server/gizmoapp_server/capabilities/` contains lazy backend integrations for audio, search, optimization, OpenStreetMap, and optional scikit-learn
- `server/gizmoapp_server/static/app/capabilities/` contains optional frontend helpers that are not imported by default
- `scripts/` contains install, deploy, and asset-generation helpers
- `deploy/` contains example `gunicorn`, `nginx`, and cron snippets
- `docs/design-overview.md` records the intended architecture, config split, and deployment model
- `docs/agent-map.md` is the short routing guide for coding agents so they can open only the files relevant to the current task
- `docs/agent-extension-guide.md` gives future coding agents concrete extension rules
- `deploy/app-shell.txt` contains git-tracked shell intent for hosted/student workspaces without using a worker-denied `*.env` path
- `deploy/app.env` contains git-tracked deployment settings that should reach the server only through an explicitly requested push/deploy flow
- `deploy/non-scaffold-app-deployment.md` explains how existing non-GizmoApp apps should fit into the neutral nginx host layout
- `tests/` contains API and routing smoke tests

## Design Overview

The short operational instructions in this README assume the design choices in
[`docs/design-overview.md`](docs/design-overview.md). Read that file when you
need the reasoning behind:

- why there are two frontend shells in one repo
- why deployment is path-prefix-aware
- why `deploy/app-shell.txt`, `deploy/app.env`, and `.env` have different roles
- why cron deploys, user services, and nginx snippets are structured the way they are

## Deployment Model

There are now two separate deployment installation layers:

- Machine bootstrap: install the system packages needed on the host once
- App instance install: clone one specific repo/fork into a named directory, configure it, and make it serve at `vickrey10.cs.ubc.ca/name`

This split is meant to support multiple independent apps derived from this starter on the same machine.

## Local Development

1. Copy `.env.example` to `.env` if you want to change local machine-specific settings. For a local prefix test, set `GIZMOAPP_URL_PREFIX=/demo-app`.
2. Create the virtualenv and install dependencies:

```bash
ALLOW_NETWORK_INSTALL=1 make install
```

3. Initialize the SQLite database:

```bash
make init-db
```

4. Run the development server:

```bash
ALLOW_SERVER_RUN=1 make dev
```

Or start a specific shell explicitly:

```bash
ALLOW_SERVER_RUN=1 make dev-auto
ALLOW_SERVER_RUN=1 make dev-graphical
ALLOW_SERVER_RUN=1 make dev-text
```

The development commands now auto-read `deploy/app.env` and then a repo-root `.env`. The default app URL is `http://127.0.0.1:8001/` unless you set `GIZMOAPP_URL_PREFIX`, in which case the app lives under that prefix.

Run the repo-standard validation entry point with:

```bash
make validate
```

The helper first runs a Python-based JavaScript structural check, then uses `.venv`, system packages, or `.pydeps/` when they already exist. It does not install packages automatically, so it stays safe for escalation-free agent runs. Node is intentionally not required; for a JS-only sanity pass, run:

```bash
make js-check
```

Before a local source-repo commit, this helper can set a repo-local Git identity and safely clear stale index locks:

```bash
make commit-ready
```

Machine-learning features should install the optional scikit-learn dependency only when an app actually needs ML:

```bash
ALLOW_NETWORK_INSTALL=1 make install-ml
```

## Visual Verification

Graphics work should be checked with a browser screenshot pass before it is treated
as finished. The visual pipeline is optional so the base app stays lean:

```bash
ALLOW_NETWORK_INSTALL=1 make visual-install
ALLOW_BROWSER_CHECK=1 make visual-check
```

The install step may need network access, and the check step starts browser/server automation. Agents should run them only when that work is already permitted or the user explicitly asks for it. `make visual-check` starts the graphical shell, captures phone, tablet, and
desktop screenshots, checks that `#scene-canvas` is rendered, and writes:

- `var/visual-report/index.html`
- `var/visual-report/report.json`
- `var/visual-report/graphical-*.png`

Open the HTML report and inspect the screenshots. Pixel checks can catch broken
or unintentionally flat canvases, while the starter canvas may explicitly mark
itself as intentionally blank.

## Shell Selection

The project keeps both blank shells in the same codebase and shares the same backend, API, database, and deployment scripts.

- `server/wsgi_graphical.py` serves the graphical shell
- `server/wsgi_text.py` serves the text-first shell
- `server/wsgi.py` serves whichever shell is selected by `GIZMOAPP_SHELL`

On the server, the simplest approach is to keep the gunicorn target at `server.wsgi:app` and set the default shell in `deploy/app.env`. Use `GIZMOAPP_SHELL=auto` for open-ended agentic/template-derived workspaces. Auto mode inspects changed files in the checkout: text-shell template/assets select `text`, graphical template/assets select `graphical`, and mixed or unclear changes fall back to `graphical`. When a hosted CodingWorkspace app clearly chooses one public shell, set `deploy/app-shell.txt` to `text` or `graphical`; do not edit `.env` or rely on `deploy/app.env` for hosted shell intent because worker permissions may deny `*.env` edits. For non-hosted deploy flows, a concrete `GIZMOAPP_SHELL=text` or `GIZMOAPP_SHELL=graphical` in tracked `deploy/app.env` remains the env-style deployment setting. The deploy scripts merge the tracked env setting into the live `.env` and restart the service when it changes.

## Using This As A Starter

If you want future users to create their own apps from this starting point, GitHub template repositories are usually a better fit than forks.

- Use a template repository when the new project should start with the same files but become its own independent app and history.
- Use a fork when the main goal is to contribute changes back to this repository while preserving GitHub’s fork relationship.

For this repository, the intended use is as a starter/template. A derived app should usually get its own repo name, its own deployment target, and its own branding rather than staying tied to GizmoApp.

To support that use case, keep these traits intact:

- configuration lives in `.env`
- hosted shell intent lives in `deploy/app-shell.txt`
- git-controlled deployment defaults live in `deploy/app.env`
- deployment steps stay explicit in `README.md` and `deploy/`
- the backend remains shared and understandable
- shell-specific UI stays isolated so future projects can keep one shell or both

For template-derived apps, the intended workflow is:

- complete a task
- commit it with a descriptive message
- if Git identity or a stale index lock blocks the commit, run `make commit-ready` instead of changing global Git config or removing lock files by hand
- push it so the deployment cron job can pick it up only when the user explicitly asks for the push or deploy flow
- if the task installs or generates local-only files that do not belong in the repo, add them to `.gitignore`

For deployed template-derived apps, prefer this split:

- `deploy/app-shell.txt` is git-tracked and should hold hosted/student shell intent when a CodingWorkspace app clearly chooses `text` or `graphical`
- `deploy/app.env` is git-tracked and should hold non-secret runtime choices you want to reach the server through an explicit `git push` plus cron deploy flow
- `.env` on the server is machine-specific and should hold secrets, ports, DB paths, service names, and per-instance URL prefixes

For example, forcing a hosted CodingWorkspace preview from the text shell to the graphical shell should normally mean editing `deploy/app-shell.txt`. Forcing a non-hosted deployment should normally mean editing `deploy/app.env`, then committing and pushing only as part of an explicitly requested deploy flow, not SSHing into the server to edit `.env`.

## API Surface

- `GET /api/bootstrap` returns app metadata, health details, and available capability summaries
- `GET /api/capabilities` returns available capability modules and optional dependency status
- `GET /api/search?q=...` searches persisted sample records in SQLite
- `GET /api/map/default` returns OpenStreetMap settings and the default UBC Vancouver location when mapping is requested
- `GET /api/ml/status` reports whether scikit-learn is installed
- `POST /api/ml/kmeans` runs a small scikit-learn KMeans job when ML dependencies are installed
- `POST /api/optimize/route` runs a simple route ordering optimization
- `POST /api/audio/analyze` summarizes browser-captured sample arrays
- `GET /api/sample-nodes` lists optional sample records from SQLite
- `POST /api/sample-nodes` inserts an optional sample record for future experimentation
- `GET /healthz` returns a simple JSON health response
- `GET /admin/` shows a small admin summary page

If `GIZMOAPP_URL_PREFIX` is set, all of those routes live under the prefix. For example, `/demo-app/api/bootstrap`.

## Deployment Notes

The commands in this section are manual deployment actions. They may install packages, use `sudo`, write outside the checkout, contact GitHub, edit nginx, reload services, or change cron. Coding agents should not run them unless the user explicitly asks for that deployment action in the current turn.

### One-time machine bootstrap

Run this once per deployment machine:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_machine_dependencies.sh
```

This installs the required Ubuntu/Debian packages such as Python, `python3-venv`, Git, SQLite, curl, and cron.

### One-time nginx bootstrap for single-command future deployments

If you want future app installs to become one command with no manual nginx edits,
run this once on the server:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_nginx_instance_router.sh \
  --server-config /etc/nginx/sites-enabled/vickrey10 \
  --server-name vickrey10.cs.ubc.ca
```

That creates a managed nginx include directory at `/etc/nginx/gizmoapp-instances`,
patches the chosen site config to include `*.conf` files from that directory inside
the matching `server` block, validates nginx, and reloads it.

If your site file does not contain an explicit `server_name vickrey10.cs.ubc.ca`
line but the file itself is clearly the right site config and contains only one
`server { ... }` block, you can omit `--server-name` and point directly at that
file:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_nginx_instance_router.sh \
  --server-config /etc/nginx/sites-enabled/vickrey10
```

After that one-time bootstrap, future `install_deployment_instance.sh` runs will
copy each app's generated snippet into `/etc/nginx/gizmoapp-instances/<name>.conf`
and reload nginx automatically.

### Recommended nginx layout on `vickrey10.cs.ubc.ca`

For long-term clarity, do not use an app-specific nginx filename such as
`/etc/nginx/sites-enabled/ai100` as the permanent home for all path-based apps.
Prefer this structure instead:

- neutral host file:
  - `/etc/nginx/sites-available/vickrey10`
  - `/etc/nginx/sites-enabled/vickrey10`
- one snippet per routed app:
  - `/etc/nginx/gizmoapp-instances/AI100.conf`
  - `/etc/nginx/gizmoapp-instances/gizmotest.conf`
  - `/etc/nginx/gizmoapp-instances/myapp.conf`

An example neutral host file is provided at `deploy/nginx-host.example.conf`.
That file owns the host-level `server { ... }` block and includes
`/etc/nginx/gizmoapp-instances/*.conf`.

### Safe migration from `ai100` to a neutral `vickrey10` host file

If the current live path `/AI100` is still served from an nginx file named
`/etc/nginx/sites-enabled/ai100`, migrate in this order so `/AI100` keeps
working throughout:

1. Create the managed snippet directory once. This is a manual server-admin step
   that writes under `/etc/nginx`.

2. Create `/etc/nginx/gizmoapp-instances/AI100.conf` containing the existing
`/AI100` location block. If `~/bin/AI100` is based on this scaffold, you can
reuse its generated snippet or match the existing live config exactly.

3. Create a neutral host config file from `deploy/nginx-host.example.conf`.

4. Adjust the copied host file if needed for your host-level defaults, then enable it.

5. Validate nginx and confirm `/AI100/` still responds before removing the old file.

6. Only after `/AI100/` still works through the new host file, disable the old
app-named site file if it is no longer needed, validate nginx again, and reload it.

After that migration, run the one-time router bootstrap against the neutral host file:

```bash
cd /home/kevinlb/bin/GizmoApp
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_nginx_instance_router.sh \
  --server-config /etc/nginx/sites-enabled/vickrey10
```

From that point on, future app installs can register themselves automatically
without editing nginx by hand.

For the current server, a more direct migration helper is available:

```bash
cd /home/kevinlb/bin/GizmoApp
ALLOW_DEPLOY_ACTIONS=1 ./scripts/migrate_nginx_to_neutral_host.sh
```

That helper is tailored to the existing `ai100` to `vickrey10` rename and will:

- copy the live enabled site from `/etc/nginx/sites-enabled/ai100`
- create `/etc/nginx/sites-available/vickrey10`
- enable `/etc/nginx/sites-enabled/vickrey10`
- disable the old `/etc/nginx/sites-enabled/ai100` path
- bootstrap `/etc/nginx/gizmoapp-instances/*.conf`
- validate and reload nginx

Because it copies the current live host config first, the existing `/AI100`
route should keep working after the migration. That route may remain inline in
the neutral host file until you choose to normalize it into its own managed
snippet.

If you have already-installed app instances that predate automatic nginx
registration, register them once with:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/register_nginx_instance_snippet.sh \
  --name gizmotest \
  --snippet /home/kevinlb/bin/gizmotest/var/generated/nginx-location.conf
```

### Current-checkout install

If the current checkout is itself the live deployment checkout, run:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_server.sh
```

That convenience wrapper runs both the machine bootstrap and the current-checkout initialization.

If machine dependencies are already installed and you only want to initialize the current checkout, run:

```bash
ALLOW_NETWORK_INSTALL=1 ./scripts/install_checkout.sh
```

That script also normalizes `.env` to owner-only permissions so secrets do not stay world-readable on shared machines, and merges any git-tracked settings from `deploy/app.env` into the live `.env`.

### Install a fork/template-derived app at `/name`

After a derived repo exists on GitHub, install it onto the server with:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/install_deployment_instance.sh \
  --name myapp \
  --repo-url git@github.com:YOUR_ACCOUNT/YOUR_REPO.git \
  --branch main \
  --shell text
```

This script:

- creates or updates `/home/kevinlb/bin/myapp`
- checks out `origin/main`
- writes `/home/kevinlb/bin/myapp/.env`
- locks `/home/kevinlb/bin/myapp/.env` to owner-only permissions and safely quotes values such as app titles with spaces
- merges git-tracked settings from `deploy/app.env` into the live `.env`
- picks a free local gunicorn port unless you specify `--port`
- creates the virtualenv and installs Python dependencies
- initializes the SQLite database
- writes a user-level systemd service at `~/.config/systemd/user/myapp.service`
- installs a once-per-minute cron entry for `scripts/deploy_from_git.sh`
- generates an nginx location snippet at `/home/kevinlb/bin/myapp/var/generated/nginx-location.conf`, including a redirect from `/myapp` to `/myapp/`
- if the one-time nginx router bootstrap has been installed, copies the snippet into `/etc/nginx/gizmoapp-instances/myapp.conf` and reloads nginx automatically

The default public URL becomes `http://vickrey10.cs.ubc.ca/myapp/`.

### Fastest server command for new GizmoApp-derived repos

If you want a one-argument deployment command, use:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/deploy_gizmoapp_repo.sh git@github.com:YOUR_ACCOUNT/YOUR_REPO.git
```

That wrapper:

- infers the app name from the repository name
- checks the repo out under `/home/kevinlb/bin/<repo-name>`
- serves it at `http://vickrey10.cs.ubc.ca/<repo-name>/`
- uses the shell declared in `deploy/app.env`, or falls back to `auto` if that file does not set one. With `auto`, `deploy/app-shell.txt` can still pin hosted/student shell intent inside the app.
- installs the per-minute git deploy cron job
- registers the nginx route during the approved deploy action if the one-time router bootstrap has been run

For example:

```bash
ALLOW_DEPLOY_ACTIONS=1 ./scripts/deploy_gizmoapp_repo.sh git@github.com:kevinlb1/GizmoAppKLB1.git
```

To make this easy to run from anywhere on the server, a server administrator can
copy `scripts/deploy_gizmoapp_repo.sh` into `~/bin/deploy-gizmoapp-repo`.

Then future installs become:

```bash
ALLOW_DEPLOY_ACTIONS=1 ~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git
```

Optional overrides:

```bash
ALLOW_DEPLOY_ACTIONS=1 ~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git --shell text
ALLOW_DEPLOY_ACTIONS=1 ~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git --branch develop
```

### After running `install_deployment_instance.sh`

1. Review `/home/kevinlb/bin/myapp/.env`.
   Treat it as machine-specific state, not the normal place for app-level settings that should come from git.
2. If you already ran `install_nginx_instance_router.sh`, the approved installer updates nginx and you can skip to checking the service.
3. If you did not run the one-time router bootstrap, add the generated nginx snippet from `/home/kevinlb/bin/myapp/var/generated/nginx-location.conf` to the `vickrey10.cs.ubc.ca` nginx server block.
4. Reload nginx manually on the server if you edited the host config.

5. Check the user service on the server.

6. Visit `http://vickrey10.cs.ubc.ca/myapp/`.

If the app should stay running even when the deployment user is logged out, a
privileged user may also need to enable linger for the deployment account.

### `gunicorn` reload behavior

Static asset changes do not require a `gunicorn` reload because Flask serves them from disk on each request. Backend Python and template changes do require a reload so workers pick up the new code. The deploy script detects that difference and only attempts a reload when needed.

### Cron deployment

The example cron entry in `deploy/user-crontab.example` calls `scripts/deploy_from_git.sh` once per minute. That script:

- Refuses to deploy if tracked files are dirty
- Fast-forwards the live checkout from `origin/main`
- Merges git-tracked deployment settings from `deploy/app.env` into the live `.env`
- Reinstalls Python packages only when `server/requirements.txt` changes
- Re-initializes the database idempotently
- Reloads `gunicorn` when runtime files changed and a reload strategy is configured

If a pushed commit changes `deploy/app.env`, the deploy script restarts the user service so the new environment takes effect. This is the intended way to send settings such as shell changes to the server without manual SSH edits.

The installed cron entry also exports `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` so `systemctl --user` can talk to the user systemd bus even when the deploy runs from cron.

When you use `scripts/install_deployment_instance.sh` with `ALLOW_DEPLOY_ACTIONS=1`, the script installs a real cron entry for that specific checkout unless you pass `--skip-cron`.

If you have older app installs that were created before this cron hardening, re-run `scripts/install_deployment_instance.sh` for that app or update the crontab entry so it includes those two environment variables before calling `scripts/deploy_from_git.sh`.

### HTTPS and installability

Reliable PWA installation on iPhone and Chromium-based browsers requires HTTPS. If `vickrey10.cs.ubc.ca` is only available over plain HTTP, the app will still run in the browser, but install prompts and standalone behavior will be limited or unavailable.
