# ============================================================
# GUARDIAN — IAM Lockdown Template
# llm_factory.py — LLM client factory (offline + online)
# ============================================================

import json
import urllib.request
import urllib.error
from config import GUARDIAN_MODE, LOCAL_MODEL, ONLINE_MODEL


class LocalOllamaLLM:
    """
    Offline LLM wrapper using Ollama REST API.
    Requires Ollama running locally: ollama serve
    """

    def __init__(self, model: str):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"

    def call(self, prompt: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 2048
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=600) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                return data.get("response", "")
        except urllib.error.URLError as e:
            return f"ERROR: Ollama API call failed: {e}"
        except Exception as e:
            return f"ERROR: Unexpected error calling Ollama API: {e}"


class OnlineAnthropicLLM:
    """
    Online LLM wrapper using Anthropic API.
    Requires ANTHROPIC_API_KEY environment variable set.
    """

    def __init__(self, model: str):
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"

    def call(self, prompt: str) -> str:
        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if not api_key:
            return "ERROR: ANTHROPIC_API_KEY environment variable not set."

        payload = json.dumps({
            "model": self.model,
            "max_tokens": 2048,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }).encode("utf-8")

        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                return data["content"][0]["text"]
        except urllib.error.URLError as e:
            return f"ERROR: Anthropic API call failed: {e}"
        except Exception as e:
            return f"ERROR: Unexpected error calling Anthropic API: {e}"


def get_llm():
    """
    Returns the correct LLM client based on GUARDIAN_MODE in config.py.
    offline = LocalOllamaLLM (free, private, no internet needed)
    online  = OnlineAnthropicLLM (better quality, requires API key)
    """
    if GUARDIAN_MODE == "online":
        print(f"[GUARDIAN] Using online mode: {ONLINE_MODEL}")
        return OnlineAnthropicLLM(model=ONLINE_MODEL)
    else:
        print(f"[GUARDIAN] Using offline mode: {LOCAL_MODEL}")
        return LocalOllamaLLM(model=LOCAL_MODEL)
