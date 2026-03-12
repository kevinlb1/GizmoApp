# AGENTS.md

## Workflow Rules
1. When a task is complete, `git commit` the changes with a descriptive commit message, but do not push.
2. Update this `AGENTS.md` whenever a task changes important operational, deployment, workflow, or safety context.
3. Prefer changes that make future Codex edits easy: keep structure explicit, keep files reasonably small, and avoid unnecessary complexity.
4. If Git author identity is missing, prefer configuring a repo-local identity instead of changing global Git settings without explicit user direction.

## Project Intent
- This repository is intended to become a blank graphical webapp scaffold.
- The app should render in a browser and support interaction on an Amazon Fire tablet, an Apple iPhone, and desktop Chrome on a PC.
- The current priority is a clean, modifiable template rather than end-user functionality.
- The interface should stay tablet-friendly while still performing well on desktop-class Chrome.
- The app should remain anonymous and public for now, but the structure should not make later authentication work difficult.
- The frontend should be installable as an app-like PWA, but offline support is not currently required.

## Deployment Context
- Development work happens in this repository: `/home/kevinlb/programming/emmie`.
- The intended live checkout on the server is: `/home/kevinlb/bin/emmie`.
- The git remote is expected to be: `git@github.com:kevinlb1/emmie.git`.
- The public deployment target is: `vickrey10.cs.ubc.ca`.
- `gunicorn` is already running on the target machine, with `nginx` in front of it.
- The intended server automation is a once-per-minute cron job that fetches repository updates and deploys them when new commits are available.
- The deployment branch is `main`.
- The app may be hosted under a URL prefix such as `/AI100`, so routes and assets should support a configurable prefix.

## Operational Guidance
- Treat deployment automation, cron configuration, and `gunicorn` reload behavior as important operational context and record notable changes here.
- Prefer lightweight, easy-to-operate defaults unless the user chooses otherwise.
- The current template should favor a low-friction, easy-to-edit stack over unnecessary tooling.
- Use SQLite as the initial persistent store.
- Include a minimal backend API, a sample database schema, and a lightweight admin/health surface.
- Provide a manual server install script for dependencies; do not make cron responsible for first-time machine setup.
- Design deploy automation so it can fast-forward from git in user mode and reload `gunicorn` only when backend/runtime changes require it.

## Safety Guidance
- Do not push to the remote unless the user explicitly asks for it.
- Avoid making irreversible server or deployment changes without clear user direction.
- Treat HTTPS as a practical requirement for reliable PWA installation, especially on iPhone and Chromium-based browsers.

## Local Git Identity
- This repository may use the repo-local Git identity `Codex <codex@local>` for local-only commits when no user-specific identity has been configured.
