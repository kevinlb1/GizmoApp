# Agent Map

Read this after `AGENTS.md`. Use it to choose the smallest useful set of files
for the current task. Do not read every deployment, capability, or verification
file before making a first app change.

## First Choice

Choose the shell first:

| Student asks for | Start with | Edit first |
| --- | --- | --- |
| Canvas, animation, game, simulation, drawing, map-like view, sprites, rich visuals | Graphical shell | `server/gizmoapp_server/templates/index.html`, `server/gizmoapp_server/static/app/main.js`, `server/gizmoapp_server/static/app/scene.js`, `server/gizmoapp_server/static/app/styles.css` |
| Forms, lists, dashboards, text tools, records, workflow screens | Text shell | `server/gizmoapp_server/templates/index_text.html`, `server/gizmoapp_server/static/app/text/main.js`, `server/gizmoapp_server/static/app/text/styles.css` |
| Shared data, persistence, or API behavior | Backend/API | `server/gizmoapp_server/api.py`, `server/gizmoapp_server/db.py`, `server/gizmoapp_server/views.py` |
| Runtime shell choice | Shell selection | `server/gizmoapp_server/shells.py`, `server/wsgi.py`, `deploy/app.env` |

## Graphics Fast Path

For hosted CodingWorkspace visual requests, do this first:

1. Edit the graphical shell files listed above.
2. Put the main subject in `scene.js` as one or a few offscreen bitmap textures
   or loaded image sprites.
3. Render the composed subject with `drawImage`.
4. Add a few direct controls in `index.html`, wire them in `main.js`, and expose
   one renderer update method.
5. Run `make validate`.

Only open `scripts/visual_verify.py`, `server/requirements-visual.txt`, or the
Playwright report internals if screenshot verification is already available and
you need to debug that pipeline. Do not install browser tooling unless the user
explicitly asks.

## When To Read More

| Need | Read |
| --- | --- |
| Architecture or why the repo is split this way | `docs/design-overview.md` |
| Detailed feature recipes for graphics, audio, search, maps, optimization, or ML | `docs/agent-extension-guide.md` |
| Local setup and normal validation commands | `README.md` |
| Deployment, nginx, cron, service files, or server installs | `README.md` deployment sections and `deploy/` |
| Optional backend capability details | Matching file under `server/gizmoapp_server/capabilities/` |
| Optional frontend capability details | Matching file under `server/gizmoapp_server/static/app/capabilities/` |

## What To Skip Unless Asked

Skip these during ordinary app-building turns:

- nginx, cron, systemd, and deployment scripts
- machine dependency installers
- visual verification implementation internals
- optional audio, ML, map, search, or optimization capability modules that the
  user did not ask for
- historical migration or host-transition scripts

Make a visible first implementation, then broaden the search only when the
first implementation needs a capability or the tests point to a specific area.
