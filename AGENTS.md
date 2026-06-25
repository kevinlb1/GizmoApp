# AGENTS.md

## Workflow Rules
1. Standing user instruction for the GizmoApp source repository: commit completed repository changes at the end of every Codex turn with a descriptive commit message. This applies to development of GizmoApp itself, not to repositories cloned from this template.
2. Standing user instruction for template-derived repositories: do not automatically run commands that would need sandbox escalation. This includes remote Git operations, package installs, browser/server automation, sudo, deployment scripts, SSH, and writes outside the workspace unless the user explicitly asks for that action in the current turn.
3. Update this `AGENTS.md` whenever a task changes important operational, deployment, workflow, or safety context.
4. Prefer changes that make future Codex edits easy: keep structure explicit, keep files reasonably small, and avoid unnecessary complexity.
5. If Git author identity is missing, prefer configuring a repo-local identity instead of changing global Git settings without explicit user direction.
6. If a task installs or generates local-only files that should not live in the repository, add them to `.gitignore` as part of the same task.
7. When a task changes graphics, canvas rendering, visual styling, maps, images, animation, or other user-visible visuals, run visual verification before ending the turn only if the needed browser/server tooling is already available without escalation or the user explicitly approves it. Inspect `var/visual-report/index.html` and improve the result if it looks bad or the canvas checks fail. If visual verification is blocked by missing browser tooling, sandbox restrictions, or another real blocker, say so explicitly in the final response instead of calling the graphics verified.

## Hosted Mini Graphics Path

When this repo is cloned inside CodingWorkspace and the student asks for a visual/canvas app, optimize for a concrete first implementation instead of a long investigation.

1. Make the first edit in the graphical shell files:
   - `server/gizmoapp_server/templates/index.html`
   - `server/gizmoapp_server/static/app/main.js`
   - `server/gizmoapp_server/static/app/scene.js`
   - `server/gizmoapp_server/static/app/styles.css`
2. Build the requested subject as one or a few bitmap sprites. Use an offscreen `<canvas>` texture or small generated PNG/WebP asset, then render it with `drawImage`. It is fine to use gradients, noise, shadows, ellipses, and lines inside the offscreen texture generator; avoid drawing the final scene as dozens of overlapping top-level polygons/ellipses/lines.
3. Add simple HTML controls such as sliders, color inputs, or buttons in `index.html`, wire them in `main.js`, and expose a small renderer method such as `scene.setParameters(...)`.
4. Keep the turn bounded. Do not spend the whole turn reading deployment docs, nginx/cron scripts, optional capability modules, or visual verification internals unless the student request specifically needs them.
5. Validate with `make validate` when available. Run `ALLOW_BROWSER_CHECK=1 make visual-check` only if browser tooling is already available and permitted. Do not run `make visual-install` automatically; if screenshots are blocked, report that blocker clearly.
6. Before finishing, check `git status --short`. A visual-app turn should leave a real code change or a clear blocker, not only notes about what you inspected. Hosted CodingWorkspace agents should commit locally when the platform asks for that, but must not push.

## Agent Orientation

Use `docs/agent-map.md` as the routing document for future coding agents. It explains which files matter for common task types and which deployment, capability, or visual-verification files should be skipped unless the current request needs them.

## Project Intent
- This repository is intended to become a blank webapp scaffold with multiple frontend shell variants.
- The app should render in a browser and support interaction on an Amazon Fire tablet, an Apple iPhone, and desktop Chrome on a PC.
- The current priority is a clean, modifiable template rather than end-user functionality.
- The interface should stay tablet-friendly while still performing well on desktop-class Chrome.
- The app should remain anonymous and public for now, but the structure should not make later authentication work difficult.
- The frontend should be installable as an app-like PWA, but offline support is not currently required.
- The project should keep at least two blank shells in the same codebase: a graphical shell and a more standard text-first shell.
- Default shells should stay light enough for future visual work to be readable. Do not seed the starter with a busy demo scene, fish tank, flock, dashboard, sample table, or workflow mockup unless the user explicitly asks for that app content.
- The initial app render must stay genuinely blank: no seeded dots, no map/geography language, and no visible database/path/runtime diagnostics outside admin-oriented surfaces.
- The graphical shell must be sprite/bitmap-first by default, not primitive-shape-first. Preserve support for layered sprites, generated or loaded bitmap textures, and future renderer swaps; use direct canvas polygons/ellipses mainly for hit areas, debug overlays, masks, or intentionally simple vector marks.
- A core purpose of this repository is to let a future Codex session start from near-zero context and still build, explain, and deploy a useful web app for a non-expert user.

## Primary Objective
- Optimize for successful end-to-end delivery by a future Codex session, not just local code changes.
- Keep the project understandable to a non-specialist user who may ask for features in plain language and may need deployment steps phrased simply.
- Prefer scaffolding that makes future extension obvious: clear file locations, clear naming, and minimal hidden build/runtime magic.

## Default Operating Model
- Assume the user may not know the existing architecture. Briefly explain the active shell, backend, and deployment path when that context matters.
- If the user asks for a conventional business/data-entry/dashboard/content app and does not specify a shell, prefer the text shell.
- If the user asks for canvas, sprites, animation, game-like UI, rich visual interaction, or possible future 3D, prefer the graphical shell and start from bitmap textures/sprites when practical.
- Keep both shells viable unless the user explicitly asks to remove one.
- Favor simple deployable implementations over introducing heavy tooling. The current frontend strategy is intentionally build-free.
- When adding features, preserve the ability to run behind an nginx path prefix such as `/demo-app` or `/<repo-name>`.
- Treat this repository as a starter/template for future independent apps. Prefer design choices that make cloning and rebranding easy.
- For template-derived apps, keep the default agent workflow escalation-free. Prefer static inspection, unit tests using already-installed local dependencies, and repo-local edits. Do not trigger network installs, local browser automation, local dev servers, remote Git, privileged setup, or deployment unless the user asks for that specific action.
- If a requested feature depends on geographic location and the user has not given a location, assume UBC Vancouver.
- If the user requests mapping, prefer OpenStreetMap before adding a paid or account-bound mapping provider.
- If the user requests machine learning, use scikit-learn through the optional `server/requirements-ml.txt` dependency path rather than adding it to the base install.

## Architecture Snapshot
- Backend: Python `Flask`
- Database: SQLite
- Frontend shells:
  - `graphical`: canvas-first, touch-friendly, suitable for sprites/animation/richer visuals
  - `text`: standard application shell suitable for forms, lists, dashboards, and workflow UI
- App selection:
  - `server/wsgi.py` serves the shell chosen by `GIZMOAPP_SHELL`
  - `GIZMOAPP_SHELL=auto` chooses from changed shell-specific files and falls back to `graphical`
  - `server/wsgi_graphical.py` forces the graphical shell
  - `server/wsgi_text.py` forces the text shell
- Deployment shape: `nginx` in front of `gunicorn`, with a live checkout typically at `/home/kevinlb/bin/GizmoApp`

## Key Files
- `README.md`: human-readable setup and deployment instructions
- `docs/design-overview.md`: architecture and design rationale for the scaffold
- `.env.example`: runtime settings template, including `GIZMOAPP_SHELL` and `GIZMOAPP_URL_PREFIX`
- `deploy/app.env`: git-tracked deployment settings that cron should apply from pushed commits, such as `GIZMOAPP_SHELL`
- `server/manage.py`: local management commands such as `init-db`, `describe`, and `run-dev`
- `server/gizmoapp_server/shells.py`: shell definitions and shell-specific metadata
- `server/gizmoapp_server/views.py`: page routes and shell/template selection
- `server/gizmoapp_server/api.py`: JSON API routes
- `server/gizmoapp_server/db.py`: SQLite schema and DB helpers
- `server/gizmoapp_server/capabilities/`: lazy backend capability modules for audio, search, optimization, mapping, and ML
- `server/gizmoapp_server/static/app/base.css`: shared responsive design tokens and app-frame styles
- `server/gizmoapp_server/static/app/capabilities/`: optional frontend helpers for browser audio, OpenStreetMap tile helpers, ML calls, and optimization calls
- `docs/agent-extension-guide.md`: concrete extension guidance for future agentic coding tasks
- `scripts/visual_verify.py`: optional Playwright-based screenshot and canvas sanity-check pipeline for graphics work
- `server/requirements-visual.txt`: optional visual-verification dependencies
- `scripts/require_explicit_approval.sh`: shared guard for commands that may need network, browser/server automation, host writes, remote Git, sudo, or deployment access
- `scripts/install_machine_dependencies.sh`: one-time host bootstrap for system packages
- `scripts/envfile.py`: shared helper for safely reading and writing shell-compatible `.env` files
- `scripts/sync_deploy_env.sh`: merges git-tracked settings from `deploy/app.env` into the live `.env` without overwriting machine-specific values
- `scripts/install_nginx_instance_router.sh`: one-time nginx bootstrap so future instance installs can update nginx automatically
- `scripts/nginx_router_bootstrap.py`: helper that inserts the managed include into the correct nginx server block
- `scripts/migrate_nginx_to_neutral_host.sh`: temporary helper for migrating the live server from the legacy `ai100` nginx filename to a neutral `vickrey10` host file
- `scripts/register_nginx_instance_snippet.sh`: registers an already-generated app snippet into the managed nginx include directory
- `scripts/deploy_gizmoapp_repo.sh`: single-command wrapper that infers name/path/url from a GizmoApp-derived repo URL and calls the main installer
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
- Read `AGENTS.md` and `docs/agent-map.md` before making architectural assumptions. Then read only the narrower docs or source files that match the current task. Do not read `README.md`, `docs/design-overview.md`, deployment scripts, or optional capability modules in detail unless the task needs them.
- Check which shell is active or intended by inspecting `.env`, `GIZMOAPP_SHELL`, or the gunicorn target.
- Prefer `GIZMOAPP_SHELL=auto` for agentic/student workspaces so the preview follows the shell-specific files that were changed.
- For template-derived apps, prefer changing git-tracked runtime settings in `deploy/app.env`; push or deploy only when the user explicitly asks for that in the current turn.
- If the user asks for a feature, decide first whether it belongs in the graphical shell, the text shell, or shared backend/API code.
- For sound, search, optimization, mapping, machine-learning, or rich-graphics work, check `docs/agent-extension-guide.md` and the capability modules before adding new infrastructure.
- Preserve deployability while editing: if runtime behavior, dependencies, routes, or operational steps change, update `README.md` and this file.
- Keep local install artifacts and machine-specific files out of Git; update `.gitignore` when new ones appear.
- Before saying validation is blocked by missing local Python packages, run `make validate`. That helper should reuse `.venv`, system packages, or repo-local `.pydeps/` when already present, but it must not install packages automatically.
- For graphics or visual UI changes, run `ALLOW_BROWSER_CHECK=1 make visual-check` only when browser/server automation is already permitted and Playwright/Chromium are already available. Do not run `make visual-install` automatically; if visual tooling is missing, report the blocker and the manual setup command.
- After completing work in the GizmoApp source repository, run the relevant validation you can run locally and create a local Git commit. For template-derived apps, commit or push only when the user explicitly asks for that Git action in the current turn.

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
- The app may be hosted under a URL prefix such as `/demo-app` or `/<repo-name>`, so routes and assets should support a configurable prefix.
- Multiple independent derived apps may be deployed on the same host under different path prefixes such as `/todoapp` or `/scoreboard`.
- Deployment scripts treat `.env` as shell-compatible configuration, not arbitrary shell code. Keep `.env` values compatible with `scripts/envfile.py`.
- For template-derived deployments, treat `deploy/app.env` as the git-controlled source of truth for non-secret runtime choices such as `GIZMOAPP_SHELL`.
- Treat the live `.env` on the server as machine-specific state for secrets, ports, DB paths, service names, and per-instance URL prefixes.
- The intended low-friction production shape is: run the one-time nginx router bootstrap once, then let each future per-instance install register its own nginx snippet automatically.
- Prefer a neutral host config file such as `/etc/nginx/sites-enabled/vickrey10`, not an app-named file such as `ai100`, as the long-term home for path-based routing.
- Non-scaffold apps should usually keep their own runtime/service/deploy process and only share the neutral nginx host layout plus one snippet per app route.

## Operational Guidance
- Treat deployment automation, cron configuration, and `gunicorn` reload behavior as important operational context and record notable changes here.
- Prefer lightweight, easy-to-operate defaults unless the user chooses otherwise.
- The current template should favor a low-friction, easy-to-edit stack over unnecessary tooling.
- Use SQLite as the initial persistent store.
- Include a minimal backend API, migration-backed SQLite schema, app state/event tables, and a lightweight admin/health surface.
- Keep optional capabilities lazy: unused ML, map, audio, graphics, and optimization helpers should not impose startup or install overhead.
- For graphical features, prefer sprite sheets, loaded/generated bitmap textures, or image-generated assets as the default visual representation. Codex can produce sprite bitmap assets when image generation is available; otherwise use procedural bitmap textures or small repo-native generated PNGs.
- Keep the visual verification pipeline optional but maintained. The base app should not require Playwright at runtime, and agents should not install Playwright or browsers unless the user explicitly approves setup that may need network access.
- Use OpenStreetMap for requested mapping features unless the user explicitly asks for another provider.
- For requested location-dependent defaults, assume UBC Vancouver unless the user gives another location.
- Use scikit-learn for ML requests, but keep it out of the base requirements so non-ML apps stay lean.
- Escalation-prone entry points must require explicit allow flags:
  - `ALLOW_NETWORK_INSTALL=1` for package installs such as `make install`, `make install-ml`, `make visual-install`, or `scripts/install_checkout.sh`
  - `ALLOW_SERVER_RUN=1` for local development server targets
  - `ALLOW_BROWSER_CHECK=1` for Playwright/browser visual checks
  - `ALLOW_DEPLOY_ACTIONS=1` for deploy, host setup, nginx, cron, systemd, remote Git, or writes outside the checkout
- Provide a manual server install script for dependencies; do not make cron responsible for first-time machine setup.
- Design deploy automation so it can fast-forward from git in user mode and reload `gunicorn` only when backend/runtime changes require it.
- A push to the app repository is the normal way for a user-approved deploy flow to send template-managed runtime changes to the server. Avoid requiring manual SSH edits for settings such as shell selection.
- Cron-driven deploys that use `systemctl --user` need the user bus environment. Keep `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` wired into the installed cron entry and into any fallback reload logic.
- Keep shell variants sharing the same backend and deployment path where practical; selecting which shell is served should be a deployment choice, not a repo split.
- If dependencies, runtime commands, route prefixes, or deployment steps change, update `.env.example`, `README.md`, deploy examples, and this file together.
- Prefer GitHub template-repository usage over forks when this codebase is being reused as a starting point for independent apps.
- Preserve the current simple mental model:
  - install host packages once with `scripts/install_machine_dependencies.sh`
  - install a specific checkout with `scripts/install_checkout.sh` or `scripts/install_deployment_instance.sh`
  - choose the git-tracked default shell with `deploy/app.env`; use `auto` unless there is a clear reason to force `graphical` or `text`
  - serve with gunicorn
  - let cron run `scripts/deploy_from_git.sh`
- Static asset changes generally do not require a gunicorn reload; Python code and templates generally do.
- For derived apps, prefer `scripts/install_deployment_instance.sh` over hand-editing service files and cron entries.
- Installers should leave `.env` at mode `600` so secrets do not become world-readable.
- The generated nginx snippet for per-instance installs should handle both `/<name>` and `/<name>/`.
- After the one-time `scripts/install_nginx_instance_router.sh` bootstrap, future app installs should not require manual nginx file edits.
- The easiest intended server UX for new GizmoApp-derived apps is: `deploy_gizmoapp_repo.sh REPO_URL`, optionally copied into `~/bin`.
- When migrating an existing app-specific nginx host file such as `ai100`, preserve the existing `/AI100` route before disabling the old site file, either by leaving the copied route inline temporarily or by moving it into `/etc/nginx/gizmoapp-instances/AI100.conf`.
- For the current server transition, a temporary scripted path exists: `scripts/migrate_nginx_to_neutral_host.sh` copies the live `ai100` host config to `vickrey10`, then bootstraps managed instance includes so `/AI100` keeps working while future apps stop depending on the `ai100` filename.

## Deployment Checklist
- The canonical starter checkout may live at `/home/kevinlb/bin/GizmoApp`, but derived app instances should usually live at `/home/kevinlb/bin/<name>`.
- Copy `.env.example` to `.env` on the server and set at least:
  - `GIZMOAPP_URL_PREFIX` if the app is mounted under a prefix such as `/<repo-name>`
  - a real `GIZMOAPP_SECRET_KEY`
- Put git-controlled runtime choices such as `GIZMOAPP_SHELL` in `deploy/app.env`; commit and push them only during an explicitly requested Git/deploy flow so cron can apply them on the server.
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
- For graphics work, do not rely only on code inspection or unit tests. Capture screenshots, inspect the rendered result, and iterate until the output is coherent across phone, tablet, and desktop viewports.
- For graphical work, start with bitmaps and sprites where possible. Avoid building finished visuals entirely from ad hoc polygon/ellipse drawing unless the requested style is explicitly vector/simple.
- Avoid introducing a frontend build step unless the user explicitly wants the tradeoff.
- Keep deployment automation understandable and inspectable by a future agent reading only this repo.
- When adding starter-friendly functionality, keep rebranding effort low: avoid scattering project-name-specific strings through shared logic unless necessary.

## Safety Guidance
- The user has explicitly requested that template-derived repository defaults avoid escalation requests. Local commits are expected for GizmoApp source-repository development. Do not push, fetch, install packages, start browser/server automation, run sudo, SSH, or deploy unless the user explicitly asks for that action in the current turn.
- Keep deployment scripts manual and opt-in. Avoid making irreversible server or deployment changes without clear user direction.
- Treat HTTPS as a practical requirement for reliable PWA installation, especially on iPhone and Chromium-based browsers.

## Local Git Identity
- This repository may use the repo-local Git identity `Codex <codex@local>` for local-only commits when no user-specific identity has been configured.
