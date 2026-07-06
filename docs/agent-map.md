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
| Runtime shell choice | Shell selection | `server/gizmoapp_server/shells.py`, `server/wsgi.py`, `deploy/app-shell.txt`, `deploy/app.env` |

When a request clearly targets one public shell, update the tracked
`deploy/app-shell.txt` value to `text` or `graphical` in the same commit as the
shell-specific UI changes. Do not edit `.env`; hosted CodingWorkspace treats it
as private runtime state and may deny access to it. Do not use `deploy/app.env`
for hosted shell intent because worker permissions may deny `*.env` edits.

The public shells intentionally have no scaffold chrome: no header, Admin
button, Install button, status pill, or starter dock. Admin remains available at
the direct `/admin/` route for development and diagnostics.

## Graphics Fast Path

For hosted CodingWorkspace visual requests, do this first:

1. Edit the graphical shell files listed above.
2. Add only the app-specific controls the user requested; do not start from
   scaffold Admin/Install/status controls.
3. If the request asks for a realistic animal, person, product, or other
   art-quality subject, use a supplied or generated PNG/WebP sprite when an
   image-generation tool or asset is available. Put durable assets under
   `server/gizmoapp_server/static/app/assets/`.
4. If no image asset source is available, make that blocker explicit and create
   an asset slot or simple stylized placeholder. Do not fake realism with dozens
   of visible ellipses, polygons, and lines.
5. Put the main subject in `scene.js` as one or a few loaded image sprites or
   offscreen bitmap textures.
6. Render the composed subject with `drawImage`.
7. Add a few direct controls in `index.html`, wire them in `main.js`, and expose
   one renderer update method.
8. Keep `createSpriteTexture` in `scene.js` unless you deliberately update
   `tests/test_graphics_defaults.py`; that helper name is a test-backed signal
   that the renderer is still sprite/bitmap-first.
9. Run `make validate`.

Use SVG/vector graphics only when the requested style is deliberately stylized
or when a simple deformable rig is more important than photoreal appearance.
Do not make a photoreal subject by stacking many SVG/canvas primitives. For
clean resize plus limited deformation, use a hybrid: high-resolution bitmap
sprite for the artwork, vector masks/handles for pose or parameter controls.

Only open `scripts/visual_verify.py`, `server/requirements-visual.txt`, or the
Playwright report internals if screenshot verification is already available and
you need to debug that pipeline. Do not install browser tooling unless the user
explicitly asks.

## Validation And Commit Rails

- Do not try to install or call Node just to check JavaScript. Use `make validate`
  for the repo-standard check or `make js-check` for the Python-based JavaScript
  structural check.
- If Git reports missing author identity or a stale `.git/index.lock`, run
  `make commit-ready`. It sets repo-local `Codex <codex@local>` identity and
  removes only stale index locks.
- In the GizmoApp source repository, commit completed changes at the end of each
  turn. In template-derived apps, do not push unless the user asks for that Git
  or deploy action.

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
