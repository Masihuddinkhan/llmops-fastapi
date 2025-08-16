import os
import requests

# Ollama config via env vars (default values for local setup)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


def ask_llm(prompt: str) -> str:
    """
    Send prompt to local Ollama model and return response.
    - Default model: gemma:2b (can be changed by OLLAMA_MODEL env var)
    - Requires `ollama serve` running in background
    """
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,   # Factual answers
                    "top_p": 0.9,
                    "num_predict": 512
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return f"[LLM Error] Could not connect to Ollama at {OLLAMA_HOST}. Is 'ollama serve' running?"
    except Exception as e:
        return f"[LLM Error] {str(e)}"