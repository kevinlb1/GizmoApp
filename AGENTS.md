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

## Deployment Context
- Development work happens in this repository: `/home/kevinlb/programming/emmie`.
- The intended live checkout on the server is: `/home/kevinlb/bin/emmie`.
- The git remote is expected to be: `git@github.com:kevinlb1/emmie.git`.
- The public deployment target is: `vickrey10.cs.ubc.ca`.
- `gunicorn` is already running on the target machine.
- The intended server automation is a once-per-minute cron job that fetches repository updates and deploys them when new commits are available.

## Operational Guidance
- Treat deployment automation, cron configuration, and `gunicorn` reload behavior as important operational context and record notable changes here.
- Prefer lightweight, easy-to-operate defaults unless the user chooses otherwise.
- Do not assume final framework, database, or build tooling choices until they are confirmed.

## Safety Guidance
- Do not push to the remote unless the user explicitly asks for it.
- Avoid making irreversible server or deployment changes without clear user direction.

## Local Git Identity
- This repository may use the repo-local Git identity `Codex <codex@local>` for local-only commits when no user-specific identity has been configured.
