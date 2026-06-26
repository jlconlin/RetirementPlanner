"""Optional local AI help backed by Ollama."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
FALSE_VALUES = {"0", "false", "no", "off", "disabled"}
TRUE_VALUES = {"1", "true", "yes", "on", "enabled"}


class AIHelpError(RuntimeError):
    """Raised when local AI help cannot complete a request."""


def _env_flag(name: str) -> bool | None:
    value = os.environ.get(name)
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return None


def ai_help_enabled() -> bool:
    """Return whether optional AI help should be shown."""
    configured = _env_flag("AI_HELP_ENABLED")
    if configured is not None:
        return configured

    runtime_env = os.environ.get("STREAMLIT_RUNTIME_ENV", "").strip().lower()
    sharing_mode = os.environ.get("STREAMLIT_SHARING_MODE", "").strip().lower()
    if runtime_env == "cloud" or sharing_mode:
        return False

    return True


def ai_help_config() -> dict[str, str]:
    """Return local AI settings from the environment."""
    return {
        "provider": os.environ.get("AI_HELP_PROVIDER", "ollama").strip().lower(),
        "base_url": os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/"),
        "model": os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip(),
    }


def scenario_snapshot(scenario: dict[str, Any]) -> dict[str, Any]:
    """Keep only assumption values useful for explaining inputs."""
    keys = [
        "current_age",
        "life_expectancy",
        "target_retirement_age",
        "current_savings",
        "annual_contribution",
        "contribution_growth_rate",
        "inflation_rate",
        "pre_retirement_return",
        "post_retirement_return",
        "return_volatility",
        "annual_expenses",
        "spending_is_after_tax",
        "tax_mode",
        "retirement_effective_tax_rate",
        "spending_model",
        "social_security_monthly",
        "social_security_start_age",
        "has_pension",
        "pension_monthly",
        "pension_start_age",
        "has_spouse",
        "spouse_age",
        "spouse_life_expectancy",
        "spouse_retirement_age",
        "survivor_spending_pct",
        "spouse_ss_monthly",
        "spouse_ss_start_age",
    ]
    return {key: scenario.get(key) for key in keys if key in scenario}


def build_ai_prompt(
    question: str,
    scenario: dict[str, Any],
    selected_input: str,
    help_text: str,
) -> list[dict[str, str]]:
    """Build a constrained chat prompt for retirement-planner input help."""
    system = (
        "You help users understand inputs in a personal retirement planning "
        "calculator. Explain assumptions, reasonable ways to estimate values, "
        "and model limitations. Do not give personalized financial, tax, legal, "
        "or investment advice. Do not recommend specific securities or portfolio "
        "allocations. If an answer depends on records or official estimates, say "
        "what source to check. Keep the answer concise and practical."
    )
    user = {
        "selected_input": selected_input,
        "input_help_text": help_text,
        "user_question": question,
        "scenario_values": scenario_snapshot(scenario),
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, indent=2, sort_keys=True)},
    ]


def ask_ollama(
    question: str,
    scenario: dict[str, Any],
    selected_input: str,
    help_text: str,
    *,
    base_url: str | None = None,
    model: str | None = None,
    timeout: float = 60.0,
) -> str:
    """Ask a local Ollama model for input help."""
    config = ai_help_config()
    base = (base_url or config["base_url"]).rstrip("/")
    selected_model = model or config["model"]
    if not selected_model:
        raise AIHelpError("No Ollama model configured.")

    payload = {
        "model": selected_model,
        "messages": build_ai_prompt(question, scenario, selected_input, help_text),
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 500,
        },
    }
    request = urllib.request.Request(
        f"{base}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise AIHelpError(
            "Could not reach Ollama. Install Ollama, pull a model, and make sure "
            "it is running at the configured OLLAMA_BASE_URL."
        ) from exc

    try:
        data = json.loads(raw)
        answer = data["message"]["content"].strip()
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise AIHelpError("Ollama returned an unexpected response.") from exc

    if not answer:
        raise AIHelpError("Ollama returned an empty answer.")
    return answer


def ask_ai_help(
    question: str,
    scenario: dict[str, Any],
    selected_input: str,
    help_text: str,
) -> str:
    """Ask the configured AI provider for input help."""
    if not question.strip():
        raise AIHelpError("Enter a question first.")

    config = ai_help_config()
    if config["provider"] != "ollama":
        raise AIHelpError(f"Unsupported AI_HELP_PROVIDER: {config['provider']}")

    return ask_ollama(question, scenario, selected_input, help_text)
