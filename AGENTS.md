# AGENTS.md

## Workflow Rules
1. When a task is complete, `git commit` the changes with a descriptive commit message, but do not push.
2. Update this `AGENTS.md` whenever a task changes important operational, deployment, workflow, or safety context.
3. Prefer changes that make future Codex edits easy: keep structure explicit, keep files reasonably small, and avoid unnecessary complexity.
4. If Git author identity is missing, prefer configuring a repo-local identity instead of changing global Git settings without explicit user direction.

## Project Intent
- This repository is intended to become a blank webapp scaffold with multiple frontend shell variants.
- The app should render in a browser and support interaction on an Amazon Fire tablet, an Apple iPhone, and desktop Chrome on a PC.
- The current priority is a clean, modifiable template rather than end-user functionality.
- The interface should stay tablet-friendly while still performing well on desktop-class Chrome.
- The app should remain anonymous and public for now, but the structure should not make later authentication work difficult.
- The frontend should be installable as an app-like PWA, but offline support is not currently required.
- The project should keep at least two blank shells in the same codebase: a graphical shell and a more standard text-first shell.
- A core purpose of this repository is to let a future Codex session start from near-zero context and still build, explain, and deploy a useful web app for a non-expert user.

## Primary Objective
- Optimize for successful end-to-end delivery by a future Codex session, not just local code changes.
- Keep the project understandable to a non-specialist user who may ask for features in plain language and may need deployment steps phrased simply.
- Prefer scaffolding that makes future extension obvious: clear file locations, clear naming, and minimal hidden build/runtime magic.

## Default Operating Model
- Assume the user may not know the existing architecture. Briefly explain the active shell, backend, and deployment path when that context matters.
- If the user asks for a conventional business/data-entry/dashboard/content app and does not specify a shell, prefer the text shell.
- If the user asks for canvas, sprites, animation, game-like UI, rich visual interaction, or possible future 3D, prefer the graphical shell.
- Keep both shells viable unless the user explicitly asks to remove one.
- Favor simple deployable implementations over introducing heavy tooling. The current frontend strategy is intentionally build-free.
- When adding features, preserve the ability to run behind an nginx path prefix such as `/AI100`.
- Treat this repository as a starter/template for future independent apps. Prefer design choices that make cloning and rebranding easy.

## Architecture Snapshot
- Backend: Python `Flask`
- Database: SQLite
- Frontend shells:
  - `graphical`: canvas-first, touch-friendly, suitable for sprites/animation/richer visuals
  - `text`: standard application shell suitable for forms, lists, dashboards, and workflow UI
- App selection:
  - `server/wsgi.py` serves the shell chosen by `GIZMOAPP_SHELL`
  - `server/wsgi_graphical.py` forces the graphical shell
  - `server/wsgi_text.py` forces the text shell
- Deployment shape: `nginx` in front of `gunicorn`, with a live checkout typically at `/home/kevinlb/bin/GizmoApp`

## Key Files
- `README.md`: human-readable setup and deployment instructions
- `.env.example`: runtime settings template, including `GIZMOAPP_SHELL` and `GIZMOAPP_URL_PREFIX`
- `server/manage.py`: local management commands such as `init-db`, `describe`, and `run-dev`
- `server/gizmoapp_server/shells.py`: shell definitions and shell-specific metadata
- `server/gizmoapp_server/views.py`: page routes and shell/template selection
- `server/gizmoapp_server/api.py`: JSON API routes
- `server/gizmoapp_server/db.py`: SQLite schema, seeding, and DB helpers
- `scripts/install_machine_dependencies.sh`: one-time host bootstrap for system packages
- `scripts/envfile.py`: shared helper for safely reading and writing shell-compatible `.env` files
- `scripts/install_nginx_instance_router.sh`: one-time nginx bootstrap so future instance installs can update nginx automatically
- `scripts/nginx_router_bootstrap.py`: helper that inserts the managed include into the correct nginx server block
- `scripts/migrate_nginx_to_neutral_host.sh`: temporary helper for migrating the live server from the legacy `ai100` nginx filename to a neutral `vickrey10` host file
- `scripts/register_nginx_instance_snippet.sh`: registers an already-generated app snippet into the managed nginx include directory
- `scripts/install_checkout.sh`: initialize the current checkout after machine dependencies exist
- `scripts/install_deployment_instance.sh`: install one named deployment instance from a repo URL
- `scripts/install_server.sh`: compatibility wrapper that runs machine bootstrap plus current-checkout install
- `scripts/deploy_from_git.sh`: cron-friendly fast-forward deploy script
- `deploy/gizmoapp-gunicorn.service.example`: example user service
- `deploy/nginx-host.example.conf`: example neutral nginx host config that includes one snippet per path-based app
- `deploy/nginx-location.example.conf`: example nginx location block
- `deploy/non-scaffold-app-deployment.md`: instructions for apps such as `AI100` that are not managed by the GizmoApp scaffold
- `deploy/user-crontab.example`: example once-per-minute deployment cron entry

## First Steps For A Fresh Session
- Read `AGENTS.md` and `README.md` before making architectural assumptions.
- Check which shell is active or intended by inspecting `.env`, `GIZMOAPP_SHELL`, or the gunicorn target.
- If the user asks for a feature, decide first whether it belongs in the graphical shell, the text shell, or shared backend/API code.
- Preserve deployability while editing: if runtime behavior, dependencies, routes, or operational steps change, update `README.md` and this file.
- After completing work, run the relevant validation you can run locally and then commit without pushing.

## Non-Expert User Support
- Use plain language when describing choices, especially around shell selection, deployment, gunicorn, nginx, cron, and SQLite.
- When the user is unsure, recommend one concrete path instead of giving many equal options.
- If a task spans coding plus deployment, make the repo changes first, then leave a short checklist the user can execute on the server.
- Avoid requiring the user to understand internal framework details unless those details affect a decision they must make.

## Deployment Context
- Development work happens in the current repository root. Do not assume the local checkout directory name is authoritative if the repo was renamed after cloning.
- The intended live checkout on the server is: `/home/kevinlb/bin/GizmoApp`.
- The canonical git remote after the GitHub rename is expected to be: `git@github.com:kevinlb1/GizmoApp.git`.
- The public deployment target is: `vickrey10.cs.ubc.ca`.
- `gunicorn` is already running on the target machine, with `nginx` in front of it.
- The intended server automation is a once-per-minute cron job that fetches repository updates and deploys them when new commits are available.
- The deployment branch is `main`.
- The app may be hosted under a URL prefix such as `/AI100`, so routes and assets should support a configurable prefix.
- Multiple independent derived apps may be deployed on the same host under different path prefixes such as `/todoapp` or `/scoreboard`.
- Deployment scripts treat `.env` as shell-compatible configuration, not arbitrary shell code. Keep `.env` values compatible with `scripts/envfile.py`.
- The intended low-friction production shape is: run the one-time nginx router bootstrap once, then let each future per-instance install register its own nginx snippet automatically.
- Prefer a neutral host config file such as `/etc/nginx/sites-enabled/vickrey10`, not an app-named file such as `ai100`, as the long-term home for path-based routing.
- Non-scaffold apps should usually keep their own runtime/service/deploy process and only share the neutral nginx host layout plus one snippet per app route.

## Operational Guidance
- Treat deployment automation, cron configuration, and `gunicorn` reload behavior as important operational context and record notable changes here.
- Prefer lightweight, easy-to-operate defaults unless the user chooses otherwise.
- The current template should favor a low-friction, easy-to-edit stack over unnecessary tooling.
- Use SQLite as the initial persistent store.
- Include a minimal backend API, a sample database schema, and a lightweight admin/health surface.
- Provide a manual server install script for dependencies; do not make cron responsible for first-time machine setup.
- Design deploy automation so it can fast-forward from git in user mode and reload `gunicorn` only when backend/runtime changes require it.
- Keep shell variants sharing the same backend and deployment path where practical; selecting which shell is served should be a deployment choice, not a repo split.
- If dependencies, runtime commands, route prefixes, or deployment steps change, update `.env.example`, `README.md`, deploy examples, and this file together.
- Prefer GitHub template-repository usage over forks when this codebase is being reused as a starting point for independent apps.
- Preserve the current simple mental model:
  - install host packages once with `scripts/install_machine_dependencies.sh`
  - install a specific checkout with `scripts/install_checkout.sh` or `scripts/install_deployment_instance.sh`
  - choose shell with `GIZMOAPP_SHELL`
  - serve with gunicorn
  - let cron run `scripts/deploy_from_git.sh`
- Static asset changes generally do not require a gunicorn reload; Python code and templates generally do.
- For derived apps, prefer `scripts/install_deployment_instance.sh` over hand-editing service files and cron entries.
- Installers should leave `.env` at mode `600` so secrets do not become world-readable.
- The generated nginx snippet for per-instance installs should handle both `/<name>` and `/<name>/`.
- After the one-time `scripts/install_nginx_instance_router.sh` bootstrap, future app installs should not require manual nginx file edits.
- When migrating an existing app-specific nginx host file such as `ai100`, preserve the existing `/AI100` route by moving it into `/etc/nginx/gizmoapp-instances/AI100.conf` before disabling the old site file.
- For the current server transition, a temporary scripted path exists: `scripts/migrate_nginx_to_neutral_host.sh` copies the live `ai100` host config to `vickrey10`, then bootstraps managed instance includes so `/AI100` keeps working while future apps stop depending on the `ai100` filename.

## Deployment Checklist
- The canonical starter checkout may live at `/home/kevinlb/bin/GizmoApp`, but derived app instances should usually live at `/home/kevinlb/bin/<name>`.
- Copy `.env.example` to `.env` on the server and set at least:
  - `GIZMOAPP_SHELL=graphical` or `GIZMOAPP_SHELL=text`
  - `GIZMOAPP_URL_PREFIX` if the app is mounted under a prefix such as `/AI100`
  - a real `GIZMOAPP_SECRET_KEY`
- Run `./scripts/install_server.sh` manually after the initial clone or after major environment changes.
- Configure gunicorn from `deploy/gizmoapp-gunicorn.service.example`.
- Configure nginx from `deploy/nginx-location.example.conf`.
- Configure the user cron job from `deploy/user-crontab.example`.
- If the deployment shape changes, document the new exact steps in `README.md` and summarize them here.

## Multi-App Deployment
- The host-level dependency script is `scripts/install_machine_dependencies.sh`.
- The per-instance deployment script is `scripts/install_deployment_instance.sh`.
- A deployment instance maps a repo URL plus a name to:
  - checkout directory `/home/kevinlb/bin/<name>`
  - URL prefix `/<name>`
  - user service `<name>.service`
  - its own SQLite file under that checkout
  - its own cron entry calling `scripts/deploy_from_git.sh`
- The per-instance script also generates an nginx location snippet for the chosen name and port.
- User-level systemd deployments may require `loginctl enable-linger <user>` once on the host so services survive logout.
- If a future task changes instance layout, env keys, or service generation, record it here.

## Editing Priorities
- Prefer shared backend changes when a feature should work in both shells.
- Keep shell-specific UI code under the shell’s own template and static asset directory.
- Avoid introducing a frontend build step unless the user explicitly wants the tradeoff.
- Keep deployment automation understandable and inspectable by a future agent reading only this repo.
- When adding starter-friendly functionality, keep rebranding effort low: avoid scattering project-name-specific strings through shared logic unless necessary.

## Safety Guidance
- Do not push to the remote unless the user explicitly asks for it.
- Avoid making irreversible server or deployment changes without clear user direction.
- Treat HTTPS as a practical requirement for reliable PWA installation, especially on iPhone and Chromium-based browsers.

## Local Git Identity
- This repository may use the repo-local Git identity `Codex <codex@local>` for local-only commits when no user-specific identity has been configured.
