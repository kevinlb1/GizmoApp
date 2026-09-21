# Course Image and Speech

CodingWorkspace can run small image and speech models on the course Ada GPU
workers. GizmoApp exposes them through the dependency-free, server-side helper
in `server/gizmoapp_server/media.py`.

Use this service when an app needs:

- a generated 512×512 PNG;
- fast drafts or higher-quality final image generation;
- image-to-image, mask-based, or instruction-based editing; or
- multilingual Kokoro speech synthesis as compressed MP3 audio (WAV remains available).

Coding turns may call the helper directly from Python to create requested assets.
Browser-driven app features must call a Flask route in the app. Neither path
may expose `GIZMO_MEDIA_API_KEY` in HTML, JSON, logs, SQLite, or browser storage.

## Generate an Asset During a Coding Turn

A request to generate an asset authorizes doing so now. Use the temporary media
capability already supplied to the coding process. Do not start the app, add a
button, wait for a browser action, or require a native image-generation tool.
The helper itself has no Flask dependency or application-context requirement.
From the project root:

```bash
PYTHONPATH=server/gizmoapp_server python3 - <<'PYCODE'
from pathlib import Path
from media import generate_image

result = generate_image("A red apple on a plain background", seed=7)
output = Path("server/gizmoapp_server/static/app/assets/red-apple.png")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(result.data)
print(f"Saved {output}")
PYCODE
```

Use the same direct import for `edit_image` or `synthesize_speech`; save image
bytes as `.png`; for speech use `result.file_extension` (`.mp3`, or `.wav` on an older server). Then wire the saved asset into the
requested UI using a prefix-aware static URL. Do not overwrite an existing
user asset without intent. Never print environment variables or save credentials.
If the capability is absent or expired, report that actual blocker; do not copy
an app credential from `.env` or borrow another turn's credential. Runtime-only
instructions refer to interactive app features, not requested coding-turn assets.

## Available Functions

```python
from .media import (
    CourseMediaError,
    edit_image,
    generate_image,
    synthesize_speech,
)
```

- `generate_image(prompt, model="stable-diffusion-v1-5", steps=20, seed=None)`
  returns `GeneratedMedia`. Select `model="lcm-sd15"` and `steps=8` for a fast
  draft.
- `edit_image(prompt, image, model="stable-diffusion-v1-5-img2img", strength=0.6,
  steps=20, seed=None)` accepts image
  bytes or a `pathlib.Path` and returns `GeneratedMedia`.
- `edit_image(..., model="stable-diffusion-v1-5-inpainting", mask=mask_bytes)`
  changes white mask regions while preserving black regions.
- `edit_image(..., model="instruct-pix2pix")` follows a natural-language
  editing instruction.
- `synthesize_speech(text, model="kokoro-82m", voice="af_heart",
  language="a", speed=1.0)` returns `GeneratedMedia`.

Read binary output from `result.data` and its MIME type from
`result.content_type`. Image results can also include `result.job_id` and
`result.metadata`.

`available_operations()` reports what CodingWorkspace granted to the current
coding turn or running app. The normal grant is `image.generate`, `image.edit`, and `audio.speech`.
Voice cloning is not enabled for student apps.

## Hosted Model Choices

| Task | Model | Guidance |
| --- | --- | --- |
| Fast image draft | `lcm-sd15` | Use 8 steps and iterate quickly. |
| Final image | `stable-diffusion-v1-5` | Use 15–25 steps. |
| General image variation | `stable-diffusion-v1-5-img2img` with `edit_image()` | Adjust `strength` to control how much changes. |
| Masked replacement | `stable-diffusion-v1-5-inpainting` | Supply a same-subject black/white mask; white is edited. |
| Instruction edit | `instruct-pix2pix` | Write a direct command such as “make the cat orange.” |
| Fast expressive speech | `kokoro-82m` | Preferred default. |

Kokoro language codes are `a` (American English), `b` (British English), `e`
(Spanish), `f` (French), `h` (Hindi), `i` (Italian), `p`
(Brazilian Portuguese), and `z` (Mandarin Chinese). Use a voice intended for
the selected language; invalid model voice/language combinations fail safely.

The authenticated platform endpoint `GET
${GIZMO_MEDIA_BASE_URL}/models` provides the current machine-readable catalog.
Application browser code must not call it directly because the bearer token is
server-only.

## Interactive browser media: submit and poll

Use the built-in prefix-aware `api/course-media/image`, `speech`, and `poll`
routes and `app/course-media.js`. They require the new matching CW polling
endpoint. Each route responds promptly with progress or a finished asset;
no browser request waits through model startup or the whole narration.
The platform retains the job centrally and signs a short-lived progress receipt
bound to this workspace and app credential. No secret enters JavaScript.

```javascript
const {generateMedia, narrate} = await import(
  new URL("app/course-media.js", document.baseURI)
);
// Run inside a click/submit handler; disable the button until it finishes.
const image = await generateMedia(config.apiBase, "image", {
  prompt: "A friendly robot teaching an AI class"
}, {onProgress: status => { statusElement.textContent = status; }});
imageElement.src = URL.createObjectURL(image);

// Each chunk becomes playable as soon as it is ready. Your callback should
// enqueue a chunk in the audio player, not wait for the entire narration.
await narrate(config.apiBase, narrationText, {
  voice: "af_heart",
  onProgress: ({status, index, total}) => {
    statusElement.textContent = `${status}: ${index + 1} / ${total}`;
  },
  onChunk: blob => audioQueue.push(URL.createObjectURL(blob)),
});
```

Implement the audio queue with an `<audio controls>` player: set its source to
chunk one immediately; advance to the next ready chunk on `ended`. If playback
catches up with generation, resume when another chunk arrives. Browsers may
require the user to press Play; catch rejected `play()` promises. Revoke object
URLs after playback/removal. Never concatenate WAV headers or MP3 containers.
The callback can instead save or display individual clips.

`generateMedia` polls every two seconds, tolerates transient polling outages,
and waits up to ten minutes per chunk (including cold startup). It never
retries a submission after an ambiguous response. Narration is bounded to
16,000 characters, split at whitespace into chunks of at most 500 characters,
with only one generation outstanding. Pass an AbortSignal to stop further
polling/chunks; an already submitted job may finish, but no new job is created.
Receipts expire after 15 minutes or a CW process restart. App restart/token
rotation invalidates access. A lost receipt is not recovered by resubmitting.

Python callers can use `generate_image(..., wait=False)`,
`edit_image(..., wait=False)`, or `synthesize_speech(..., wait=False)` and
`poll_media(PendingMedia)` to build custom routes. Each returns either
`PendingMedia` or `GeneratedMedia`; never send the API key to the browser.
Coding-turn asset generation keeps the synchronous default.

Existing projects are not rewritten. To adopt this in an existing app, update
`media.py`, add `media_routes.py` and `static/app/course-media.js`, register
`register_media_routes(app)` in its factory, and switch its media UI to the
helpers above. Preserve project-specific routes and content. Do not simply
increase its old 50-second fetch timeout: the outer load balancer can still
close a long idle request. Roll out CW polling support before enabling the
new app routes; an older CW image cannot serve this protocol.

## Runtime and Safety Notes

CodingWorkspace injects `GIZMO_MEDIA_BASE_URL`, `GIZMO_MEDIA_API_KEY`, and
`GIZMO_MEDIA_OPERATIONS` into an authorized coding process or app server.
Coding turns receive a separate temporary token bound to their workspace and
active turn; it stops working when the turn ends and has a bounded request
allowance. App tokens rotate when the preview restarts and are revoked when it
stops. Neither token is a central-service or worker credential; both use the
pod's authenticated local proxy. Never reuse one kind of credential for the other.

The helper validates inputs, bounds output size, waits up to five minutes by
default for worker startup and inference, and raises user-displayable
`CourseMediaError` messages. Interactive browser features must use the polling routes above; an outer
load balancer can close a long idle response even when the pod keeps it open. Requests can still report that no live GPU
worker is available; surface that message, let the user retry, and do not hide
it behind a generic network error. For runtime app features, trigger media only
after an app user action and disable duplicate submissions while one is running.
For coding-turn assets, the user's generation request is the trigger.

Current helper limits include:

- image prompts: 2,000 characters;
- speech text: 4,000 characters;
- image steps: 1–30; and
- source images for editing: 8 MB.

All current image models return 512×512 PNGs. The older M60 GPUs have limited
memory, so do not submit duplicate requests or assume a modern cloud-model
latency. Keep the previous image/audio visible while a replacement is being
generated and show a retryable busy message.

Outside CodingWorkspace the media environment variables are normally absent,
so the helper fails closed. Do not commit a real token to make local
development work.

### Speech delivery format

`synthesize_speech` requests 64 kbps mono MP3 by default. Save the returned
bytes using `result.file_extension` and serve `result.content_type`; do not
label MP3 bytes as WAV. Pass `response_format="wav"` when a tool requires PCM.
Older CW services/workers may return WAV while the rollout is in progress,
so inspect the actual result rather than assuming the requested format.
Existing projects need this helper update to opt into compressed delivery.

```python
result = synthesize_speech("Welcome to the course.")
path = media_directory / ("welcome" + result.file_extension)
path.write_bytes(result.data)
```
