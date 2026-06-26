import json
import urllib.error
from unittest.mock import patch

import pytest

from ai_help import AIHelpError, ask_ai_help, ask_ollama, build_ai_prompt


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_build_ai_prompt_includes_guardrails_and_context():
    messages = build_ai_prompt(
        "How should I estimate this?",
        {"current_age": 56, "annual_expenses": 80},
        "Annual expenses",
        "Gross annual retirement spending.",
    )

    assert messages[0]["role"] == "system"
    assert "Do not give personalized financial" in messages[0]["content"]
    payload = json.loads(messages[1]["content"])
    assert payload["selected_input"] == "Annual expenses"
    assert payload["scenario_values"]["current_age"] == 56
    assert payload["scenario_values"]["annual_expenses"] == 80


def test_ask_ollama_posts_to_local_chat_api():
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"message": {"content": "Use your actual spending."}})

    with patch("urllib.request.urlopen", fake_urlopen):
        answer = ask_ollama(
            "What should I enter?",
            {"annual_expenses": 80},
            "Annual expenses",
            "Gross annual retirement spending.",
            base_url="http://localhost:11434",
            model="llama3.2:3b",
            timeout=3,
        )

    assert answer == "Use your actual spending."
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["timeout"] == 3
    assert captured["body"]["model"] == "llama3.2:3b"
    assert captured["body"]["stream"] is False


def test_ask_ollama_reports_unavailable_service():
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", fake_urlopen):
        with pytest.raises(AIHelpError, match="Could not reach Ollama"):
            ask_ollama(
                "What should I enter?",
                {},
                "Current age",
                "Your age today.",
            )


def test_ask_ai_help_rejects_empty_question():
    with pytest.raises(AIHelpError, match="Enter a question"):
        ask_ai_help(" ", {}, "Current age", "Your age today.")
