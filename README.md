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
- `deploy/non-scaffold-app-deployment.md` explains how existing non-GizmoApp apps should fit into the neutral nginx host layout
- `tests/` contains API and routing smoke tests

## Deployment Model

There are now two separate deployment installation layers:

- Machine bootstrap: install the system packages needed on the host once
- App instance install: clone one specific repo/fork into a named directory, configure it, and make it serve at `vickrey10.cs.ubc.ca/name`

This split is meant to support multiple independent apps derived from this starter on the same machine.

## Local Development

1. Copy `.env.example` to `.env` if you want to change local settings. For a local prefix test, set `GIZMOAPP_URL_PREFIX=/demo-app`.
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

The development commands now auto-read a repo-root `.env`. The default app URL is `http://127.0.0.1:8001/` unless you set `GIZMOAPP_URL_PREFIX`, in which case the app lives under that prefix.

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

For template-derived apps, the intended workflow is:

- complete a task
- commit it with a descriptive message
- push it so the deployment cron job can pick it up, unless the user explicitly wants to keep the work local
- if the task installs or generates local-only files that do not belong in the repo, add them to `.gitignore`

## API Surface

- `GET /api/bootstrap` returns app metadata, health details, and the seeded sample nodes
- `GET /api/sample-nodes` lists the sample rows from SQLite
- `POST /api/sample-nodes` inserts a sample row for future experimentation
- `GET /healthz` returns a simple JSON health response
- `GET /admin/` shows a small admin summary page

If `GIZMOAPP_URL_PREFIX` is set, all of those routes live under the prefix. For example, `/demo-app/api/bootstrap`.

## Deployment Notes

### One-time machine bootstrap

Run this once per deployment machine:

```bash
./scripts/install_machine_dependencies.sh
```

This installs the required Ubuntu/Debian packages such as Python, `python3-venv`, Git, SQLite, curl, and cron.

### One-time nginx bootstrap for single-command future deployments

If you want future app installs to become one command with no manual nginx edits,
run this once on the server:

```bash
./scripts/install_nginx_instance_router.sh \
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
./scripts/install_nginx_instance_router.sh \
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

1. Create the managed snippet directory once:

```bash
sudo install -d -m 755 /etc/nginx/gizmoapp-instances
```

2. Create `/etc/nginx/gizmoapp-instances/AI100.conf` containing the existing
`/AI100` location block. If `~/bin/AI100` is based on this scaffold, you can
reuse its generated snippet or match the existing live config exactly.

3. Create a neutral host config file from `deploy/nginx-host.example.conf`, for example:

```bash
sudo cp /home/kevinlb/bin/GizmoApp/deploy/nginx-host.example.conf /etc/nginx/sites-available/vickrey10
```

4. Adjust the copied host file if needed for your host-level defaults, then enable it:

```bash
sudo ln -s /etc/nginx/sites-available/vickrey10 /etc/nginx/sites-enabled/vickrey10
```

5. Validate before removing the old file:

```bash
sudo nginx -t
curl -sS -D - http://vickrey10.cs.ubc.ca/AI100/ -o /dev/null
```

6. Only after `/AI100/` still works through the new host file, disable the old
app-named site file if it is no longer needed:

```bash
sudo rm /etc/nginx/sites-enabled/ai100
sudo nginx -t
sudo systemctl reload nginx
```

After that migration, run the one-time router bootstrap against the neutral host file:

```bash
cd /home/kevinlb/bin/GizmoApp
./scripts/install_nginx_instance_router.sh \
  --server-config /etc/nginx/sites-enabled/vickrey10
```

From that point on, future app installs can register themselves automatically
without editing nginx by hand.

For the current server, a more direct migration helper is available:

```bash
cd /home/kevinlb/bin/GizmoApp
./scripts/migrate_nginx_to_neutral_host.sh
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
./scripts/register_nginx_instance_snippet.sh \
  --name gizmotest \
  --snippet /home/kevinlb/bin/gizmotest/var/generated/nginx-location.conf
```

### Current-checkout install

If the current checkout is itself the live deployment checkout, run:

```bash
./scripts/install_server.sh
```

That convenience wrapper runs both the machine bootstrap and the current-checkout initialization.

If machine dependencies are already installed and you only want to initialize the current checkout, run:

```bash
./scripts/install_checkout.sh
```

That script also normalizes `.env` to owner-only permissions so secrets do not stay world-readable on shared machines.

### Install a fork/template-derived app at `/name`

After a derived repo exists on GitHub, install it onto the server with:

```bash
./scripts/install_deployment_instance.sh \
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
./scripts/deploy_gizmoapp_repo.sh git@github.com:YOUR_ACCOUNT/YOUR_REPO.git
```

That wrapper:

- infers the app name from the repository name
- checks the repo out under `/home/kevinlb/bin/<repo-name>`
- serves it at `http://vickrey10.cs.ubc.ca/<repo-name>/`
- defaults to the graphical shell
- installs the per-minute git deploy cron job
- registers the nginx route automatically if the one-time router bootstrap has been run

For example:

```bash
./scripts/deploy_gizmoapp_repo.sh git@github.com:kevinlb1/GizmoAppKLB1.git
```

To make this easy to run from anywhere on the server, copy it once into `~/bin`:

```bash
install -m 755 /home/kevinlb/bin/GizmoApp/scripts/deploy_gizmoapp_repo.sh ~/bin/deploy-gizmoapp-repo
```

Then future installs become:

```bash
~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git
```

Optional overrides:

```bash
~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git --shell text
~/bin/deploy-gizmoapp-repo git@github.com:YOUR_ACCOUNT/YOUR_REPO.git --branch develop
```

### After running `install_deployment_instance.sh`

1. Review `/home/kevinlb/bin/myapp/.env`.
2. If you already ran `install_nginx_instance_router.sh`, nginx is updated automatically and you can skip to checking the service.
3. If you did not run the one-time router bootstrap, add the generated nginx snippet from `/home/kevinlb/bin/myapp/var/generated/nginx-location.conf` to the `vickrey10.cs.ubc.ca` nginx server block.
4. Reload nginx:

```bash
sudo systemctl reload nginx
```

5. Check the user service:

```bash
systemctl --user status myapp.service
```

6. Visit `http://vickrey10.cs.ubc.ca/myapp/`.

If the app should stay running even when the deployment user is logged out, a privileged user may also need to run:

```bash
sudo loginctl enable-linger kevinlb
```

### `gunicorn` reload behavior

Static asset changes do not require a `gunicorn` reload because Flask serves them from disk on each request. Backend Python and template changes do require a reload so workers pick up the new code. The deploy script detects that difference and only attempts a reload when needed.

### Cron deployment

The example cron entry in `deploy/user-crontab.example` calls `scripts/deploy_from_git.sh` once per minute. That script:

- Refuses to deploy if tracked files are dirty
- Fast-forwards the live checkout from `origin/main`
- Reinstalls Python packages only when `server/requirements.txt` changes
- Re-initializes the database idempotently
- Reloads `gunicorn` when runtime files changed and a reload strategy is configured

When you use `scripts/install_deployment_instance.sh`, the script installs a real cron entry for that specific checkout automatically unless you pass `--skip-cron`.

### HTTPS and installability

Reliable PWA installation on iPhone and Chromium-based browsers requires HTTPS. If `vickrey10.cs.ubc.ca` is only available over plain HTTP, the app will still run in the browser, but install prompts and standalone behavior will be limited or unavailable.
