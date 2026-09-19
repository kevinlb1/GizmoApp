"""Call the course AI model from your GizmoApp.

The AI100 platform gives your running app its own AI API key through
environment variables (separate from the coding agent's key, with its own
budget, and limited to the course model):

    GIZMO_LLM_API_KEY    your app's API key (set automatically)
    GIZMO_LLM_BASE_URL   the course AI gateway
    GIZMO_LLM_MODEL      the model your app may use

Quick start, inside any view or API handler:

    from .llm import ask

    answer = ask("Write a one-line welcome message for a bakery website.")

For multi-turn conversations, build the message list yourself:

    from .llm import chat

    reply = chat([
        {"role": "system", "content": "You are a helpful cooking assistant."},
        {"role": "user", "content": "How do I know when bread is done?"},
    ])

Notes:
- A small ``max_tokens`` can make the model return an EMPTY string rather than
  an error: the request succeeds, but the budget runs out before any visible
  text is produced. If a call comes back blank, raise ``max_tokens`` before
  assuming anything is broken.
- Your app's AI budget is limited. Avoid calling the model in loops or on
  every page load; call it when the user asks for something.
"""

import os

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - dependency missing until pip install
    OpenAI = None

# Sized so a normal prompt completes rather than truncating. Measured against
# the live course model on 2026-09-19: a short story needed 875 completion
# tokens, and at 1000 an unlucky prompt returns an empty string with no error.
DEFAULT_MAX_TOKENS = 2000

_client = None


def _get_client():
    global _client
    if OpenAI is None:
        raise RuntimeError(
            "The 'openai' package is not installed. "
            "Run: pip install -r server/requirements.txt"
        )
    if not os.environ.get("GIZMO_LLM_API_KEY"):
        raise RuntimeError(
            "GIZMO_LLM_API_KEY is not set. On the AI100 platform it is provided "
            "automatically; try restarting your app (or your server session)."
        )
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["GIZMO_LLM_API_KEY"],
            base_url=os.environ.get("GIZMO_LLM_BASE_URL") or None,
        )
    return _client


def model_name():
    """The model id your app is allowed to use."""
    return os.environ.get("GIZMO_LLM_MODEL", "qwen3.6-35b-a3b")


def chat(messages, max_tokens=DEFAULT_MAX_TOKENS):
    """Send a chat-style message list; returns the assistant's reply text."""
    response = _get_client().chat.completions.create(
        model=model_name(),
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def ask(prompt, max_tokens=DEFAULT_MAX_TOKENS):
    """One-shot question in, answer text out."""
    return chat([{"role": "user", "content": prompt}], max_tokens=max_tokens)
