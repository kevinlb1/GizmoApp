"""Small fail-closed helper for the AI100 course model gateway."""

from __future__ import annotations

import os
import base64
from collections.abc import Sequence
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - dependency missing until installation
    OpenAI = None

DEFAULT_MAX_TOKENS = 2048
MAX_ALLOWED_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_TIMEOUT_SECONDS = 55.0
ALLOWED_ROLES = frozenset({"system", "user", "assistant"})
NO_THINKING = {"chat_template_kwargs": {"enable_thinking": False}}
# Tried in order, most specific first, falling back only on a 400.
NO_THINKING_ATTEMPTS = (
    {"reasoning_effort": "none", "extra_body": NO_THINKING},
    {"reasoning_effort": "none"},
    {},
)


class CourseLLMError(RuntimeError):
    """A safe, user-displayable course-model failure."""


_client = None
_client_signature: tuple[str, str, float] | None = None


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise CourseLLMError(
            f"{name} is not set. The AI100 platform supplies all course-model settings; "
            "restart the app or server session and try again."
        )
    return value


def _timeout_seconds() -> float:
    raw_value = os.environ.get("GIZMO_LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise CourseLLMError("GIZMO_LLM_TIMEOUT_SECONDS must be numeric.") from exc
    if value <= 0 or value > MAX_TIMEOUT_SECONDS:
        raise CourseLLMError(
            f"GIZMO_LLM_TIMEOUT_SECONDS must be greater than zero and at most {MAX_TIMEOUT_SECONDS:g}."
        )
    return value


def _get_client():
    global _client, _client_signature
    if OpenAI is None:
        raise CourseLLMError(
            "The 'openai' package is not installed. Run: pip install -r server/requirements.txt"
        )

    api_key = _required_environment("GIZMO_LLM_API_KEY")
    base_url = _required_environment("GIZMO_LLM_BASE_URL")
    timeout = _timeout_seconds()
    signature = (api_key, base_url, timeout)
    if _client is None or _client_signature != signature:
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=1,
        )
        _client_signature = signature
    return _client


def model_name() -> str:
    """Return the model id explicitly assigned by the course platform."""
    return _required_environment("GIZMO_LLM_MODEL")


def _validate_max_tokens(max_tokens: int) -> int:
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):
        raise CourseLLMError("max_tokens must be an integer.")
    if max_tokens < 1 or max_tokens > MAX_ALLOWED_TOKENS:
        raise CourseLLMError(f"max_tokens must be between 1 and {MAX_ALLOWED_TOKENS}.")
    return max_tokens


def _validate_messages(messages: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(messages, (str, bytes)) or not isinstance(messages, Sequence) or not messages:
        raise CourseLLMError("messages must be a non-empty sequence of message objects.")

    validated: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise CourseLLMError("each message must be an object with role and content strings.")
        role = message.get("role")
        content = message.get("content")
        if not isinstance(role, str) or role not in ALLOWED_ROLES:
            raise CourseLLMError(
                "each message must have a system, user, or assistant role and non-empty text content."
            )
        if isinstance(content, list) and content and role == "user":
            parts = []
            for part in content:
                if not isinstance(part, dict):
                    raise CourseLLMError("photo messages need text or image_url content parts.")
                if part.get("type") == "text" and isinstance(part.get("text"), str) and part["text"].strip():
                    parts.append({"type": "text", "text": part["text"]})
                elif part.get("type") == "image_url" and isinstance(part.get("image_url"), dict):
                    image = part["image_url"]
                    url = image.get("url")
                    detail = image.get("detail", "high")
                    if (not isinstance(url, str) or not url.startswith(("https://", "data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,", "data:image/gif;base64,"))
                            or not isinstance(detail, str) or detail not in {"auto", "low", "high", "original"}):
                        raise CourseLLMError("photo inputs need an HTTPS image URL or inline image and a valid detail level.")
                    parts.append({"type": "image_url", "image_url": {"url": url, "detail": detail}})
                else:
                    raise CourseLLMError("photo messages support text and image_url parts only.")
            content = parts
        elif not isinstance(content, str) or not content.strip():
            raise CourseLLMError("each message must contain non-empty text or a user photo message.")
        validated.append({"role": role, "content": content})
    return validated


def _create_completion(client: Any, **arguments: Any):
    """Create a completion, asking the model not to think out loud first.

    The course model is a reasoning model: left alone it spends the whole
    max_tokens budget on hidden reasoning and returns empty content, so the
    hints ask it to answer directly. reasoning_effort is the standard OpenAI
    parameter; chat_template_kwargs is what some gateways expect instead.
    Gateways reject what they do not recognise with a 400, so drop one at a time
    rather than all of them at once: a gateway that understands only
    reasoning_effort still gets a usable answer instead of an empty one.
    """
    last = len(NO_THINKING_ATTEMPTS) - 1
    for position, hints in enumerate(NO_THINKING_ATTEMPTS):
        try:
            return client.chat.completions.create(**arguments, **hints)
        except Exception as exc:
            if position == last or getattr(exc, "status_code", None) != 400:
                raise


def chat(messages: Sequence[dict[str, Any]], max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Send validated messages and return the assistant's text response."""
    validated_messages = _validate_messages(messages)
    validated_max_tokens = _validate_max_tokens(max_tokens)
    try:
        client = _get_client()
        response = _create_completion(
            client,
            model=model_name(),
            messages=validated_messages,
            max_tokens=validated_max_tokens,
        )
    except CourseLLMError:
        raise
    except Exception as exc:
        raise CourseLLMError(
            "The course model is temporarily unavailable. Please wait a moment and try again."
        ) from exc

    if not response.choices:
        raise CourseLLMError("The course model returned no response. Please try again.")
    content = response.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise CourseLLMError("The course model returned an empty response. Please try again.")
    return content


def ask(prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Send one user prompt to the course model."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise CourseLLMError("prompt must be non-empty text.")
    return chat([{"role": "user", "content": prompt}], max_tokens=max_tokens)


def ask_image(prompt: str, image: bytes, *, mime_type: str = "image/jpeg",
              max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
    """Ask the assigned course vision model about an uploaded photo.

    Call server-side with upload bytes; no public hosting or personal key is
    needed. This uses the course app model, not Newcastle image generation.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise CourseLLMError("prompt must be non-empty text.")
    if not isinstance(image, bytes) or not 0 < len(image) <= 8 * 1024 * 1024:
        raise CourseLLMError("photo must contain between 1 byte and 8 MB.")
    if mime_type not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        raise CourseLLMError("photo must be PNG, JPEG, WebP or a non-animated GIF.")
    data_url = f"data:{mime_type};base64," + base64.b64encode(image).decode("ascii")
    return chat([{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
    ]}], max_tokens=max_tokens)
