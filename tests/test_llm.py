from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from server.gizmoapp_server import llm


class CourseLLMTests(unittest.TestCase):
    def test_uploaded_photo_reaches_assigned_course_model(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='A tree'))])
        environment = {'GIZMO_LLM_API_KEY': 'app-key', 'GIZMO_LLM_BASE_URL': 'https://gateway.example/v1',
                       'GIZMO_LLM_MODEL': 'qwen3.6-35b-a3b'}
        with patch.dict(os.environ, environment, clear=True), patch.object(llm, 'OpenAI', Mock(return_value=client)):
            self.assertEqual(llm.ask_image('Describe this', b'photo', mime_type='image/png'), 'A tree')
        args = client.chat.completions.create.call_args.kwargs
        self.assertEqual(args['model'], 'qwen3.6-35b-a3b')
        self.assertEqual(args['messages'][0]['content'][1],
                         {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,cGhvdG8=', 'detail': 'high'}})

    def test_photo_input_validation_does_not_contact_gateway(self):
        with patch.object(llm, '_get_client') as gateway:
            for image, mime in ((b'', 'image/png'), ('photo', 'image/png'), (b'photo', 'text/html'),
                                (b'x' * (8 * 1024 * 1024 + 1), 'image/jpeg')):
                with self.subTest(mime=mime), self.assertRaises(llm.CourseLLMError):
                    llm.ask_image('Describe this', image, mime_type=mime)
            for content in ([], [{'type': 'input_audio'}], [{'type': 'image_url', 'image_url': {'url': 'file:///private'}}]):
                with self.assertRaises(llm.CourseLLMError):
                    llm.chat([{'role': 'user', 'content': content}])
            gateway.assert_not_called()

    def setUp(self):
        llm._client = None
        llm._client_signature = None

    def test_missing_gateway_or_model_fails_closed(self):
        with patch.dict(os.environ, {"GIZMO_LLM_API_KEY": "test-key"}, clear=True), patch.object(llm, "OpenAI", Mock()):
            with self.assertRaisesRegex(llm.CourseLLMError, "GIZMO_LLM_BASE_URL"):
                llm.ask("hello")

    def test_client_has_bounded_timeout_and_retry(self):
        completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello"))]
        )
        client = Mock()
        client.chat.completions.create.return_value = completion
        client_factory = Mock(return_value=client)
        environment = {
            "GIZMO_LLM_API_KEY": "test-key",
            "GIZMO_LLM_BASE_URL": "https://gateway.example/v1",
            "GIZMO_LLM_MODEL": "course-model",
            "GIZMO_LLM_TIMEOUT_SECONDS": "12",
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(llm, "OpenAI", client_factory):
            self.assertEqual(llm.ask("hello", max_tokens=100), "Hello")

        client_factory.assert_called_once_with(
            api_key="test-key",
            base_url="https://gateway.example/v1",
            timeout=12.0,
            max_retries=1,
        )
        client.chat.completions.create.assert_called_once_with(
            model="course-model",
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=100,
            reasoning_effort="none",
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

    def _gateway_rejecting(self, how_many_hints):
        """A client that answers 400 until the first `how_many_hints` are gone."""
        completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello"))]
        )
        rejections = []
        for _ in range(how_many_hints):
            rejection = Exception("unrecognised request field")
            rejection.status_code = 400
            rejections.append(rejection)
        client = Mock()
        client.chat.completions.create.side_effect = [*rejections, completion]
        return client

    def _ask_through(self, client):
        environment = {
            "GIZMO_LLM_API_KEY": "test-key",
            "GIZMO_LLM_BASE_URL": "https://gateway.example/v1",
            "GIZMO_LLM_MODEL": "course-model",
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(llm, "OpenAI", Mock(return_value=client)):
            return llm.ask("hello", max_tokens=100)

    def test_gateway_rejecting_chat_template_kwargs_keeps_reasoning_effort(self):
        """One hint is dropped at a time, so a partial gateway still gets a hint."""
        client = self._gateway_rejecting(1)
        self.assertEqual(self._ask_through(client), "Hello")

        self.assertEqual(client.chat.completions.create.call_count, 2)
        client.chat.completions.create.assert_called_with(
            model="course-model",
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=100,
            reasoning_effort="none",
        )

    def test_gateway_rejecting_every_hint_falls_back_to_a_plain_request(self):
        client = self._gateway_rejecting(2)
        self.assertEqual(self._ask_through(client), "Hello")

        self.assertEqual(client.chat.completions.create.call_count, 3)
        client.chat.completions.create.assert_called_with(
            model="course-model",
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=100,
        )

    def test_a_plain_request_that_still_fails_is_not_retried_forever(self):
        client = self._gateway_rejecting(3)
        with self.assertRaisesRegex(llm.CourseLLMError, "temporarily unavailable"):
            self._ask_through(client)
        self.assertEqual(client.chat.completions.create.call_count, 3)

    def test_gateway_outage_is_not_retried_without_the_hint(self):
        outage = Exception("service unavailable")
        outage.status_code = 503
        client = Mock()
        client.chat.completions.create.side_effect = outage
        environment = {
            "GIZMO_LLM_API_KEY": "test-key",
            "GIZMO_LLM_BASE_URL": "https://gateway.example/v1",
            "GIZMO_LLM_MODEL": "course-model",
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(llm, "OpenAI", Mock(return_value=client)):
            with self.assertRaisesRegex(llm.CourseLLMError, "temporarily unavailable"):
                llm.ask("hello", max_tokens=100)

        self.assertEqual(client.chat.completions.create.call_count, 1)

    def test_invalid_prompts_messages_and_token_limits_are_rejected(self):
        for call in (
            lambda: llm.ask(""),
            lambda: llm.chat([]),
            lambda: llm.chat([{"role": "tool", "content": "bad"}]),
            lambda: llm.ask("hello", max_tokens=0),
            lambda: llm.ask("hello", max_tokens=True),
        ):
            with self.subTest(call=call), self.assertRaises(llm.CourseLLMError):
                call()

    def test_provider_errors_are_safe_and_chained(self):
        client = Mock()
        client.chat.completions.create.side_effect = RuntimeError("secret provider detail")
        environment = {
            "GIZMO_LLM_API_KEY": "test-key",
            "GIZMO_LLM_BASE_URL": "https://gateway.example/v1",
            "GIZMO_LLM_MODEL": "course-model",
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(llm, "_get_client", return_value=client):
            with self.assertRaisesRegex(llm.CourseLLMError, "temporarily unavailable") as caught:
                llm.ask("hello")
        self.assertNotIn("secret provider detail", str(caught.exception))
        self.assertIsNotNone(caught.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
