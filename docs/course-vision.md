# Understanding photos in student apps

Use the server-side course model helper:

```python
from .llm import ask_image

answer = ask_image("Describe the objects in this photo", uploaded_bytes,
                   mime_type="image/jpeg", max_tokens=1024)
```

Read an upload with a bounded read (at most 8 MB plus one byte), validate its
type, and catch `CourseLLMError` in the app route. Show its message to the user.
Do not log or persist photos unless the app actually needs that behavior.
No public image hosting or personal API key is required. Calls stay server-side
and use `GIZMO_LLM_API_KEY`, `GIZMO_LLM_BASE_URL` and `GIZMO_LLM_MODEL` supplied by
CodingWorkspace. Never expose these credentials in browser code.

`chat()` also accepts user content lists containing `text` and `image_url`
parts. For uploaded PNG/JPEG/WebP/non-animated GIF photos, prefer `ask_image()`.
The assigned model and its gateway deployment must support image input. The
course's Qwen3.6-35B-A3B model family supports vision; actual gateway acceptance
must be verified after the platform image-input fix is deployed.

This requires the CodingWorkspace photo-input budget fix. Earlier platform
images silently replace photos with an omitted-attachment note; changing the
app alone does not repair that. Existing apps can copy this helper from the
updated starter once the platform fix is deployed. Do not tell students that
all course AI models are text-only.

Photo understanding uses the existing paid app allowance. CodingWorkspace
reserves a conservative input estimate and settles using gateway-reported
usage; image bytes are not counted as millions of text tokens. Newcastle image
generation, image editing and speech are separate, uncharged media operations
documented in `course-media.md`. They use the shared fair queue and do not
read or describe photos.
