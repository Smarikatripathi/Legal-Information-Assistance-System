import json
import os
import urllib.error
import urllib.request
from typing import Any


# =====================================================
# 1. BASE LLM CLASS
# =====================================================
class LegalLLM:
    """Wrapper for local or cloud LLM backends used by the legal RAG pipeline."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        ollama_host: str | None = None,
    ):
        self.provider = (provider or os.getenv("LEGAL_LLM_PROVIDER", "ollama")).lower()
        self.model = model or os.getenv("LEGAL_LLM_MODEL", "llama3")
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # -------------------------------------------------
    # MAIN GENERATION FUNCTION
    # -------------------------------------------------
    def generate(self, query: str, context: str) -> str:

        prompt = self.build_prompt(query, context)

        if self.provider == "openai":
            return self._openai_call(prompt)

        elif self.provider == "ollama":
            return self._ollama_call(prompt)

        else:
            return self._mock_response(prompt)

    # -------------------------------------------------
    # PROMPT ENGINEERING (VERY IMPORTANT)
    # -------------------------------------------------
    def build_prompt(self, query: str, context: str) -> str:
        return (
            "You are a legal assistant AI. Use only the provided context and do not hallucinate. "
            "Respond clearly with legal reasoning based solely on the context. "
            "If the context is insufficient, state that the documents do not contain enough information.\n\n"
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{query}\n\n"
            "Answer:"
        )

    # =====================================================
    # 2. OPENAI IMPLEMENTATION
    # =====================================================
    def _openai_call(self, prompt: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a legal assistant AI."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"OpenAI Error: {exc}"

    # =====================================================
    # 3. OLLAMA LOCAL LLM (FREE OPTION)
    # =====================================================
    def _ollama_call(self, prompt: str) -> str:
        request_body = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.ollama_host}/api/generate",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=1000) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return self._extract_ollama_response(payload)
        except urllib.error.HTTPError as exc:
            return f"Ollama HTTPError: {exc.code} {exc.reason}"
        except Exception as exc:
            return f"Ollama Error: {exc}"

    def _extract_ollama_response(self, payload: Any) -> str:
        if isinstance(payload, dict):
            if "response" in payload:
                return str(payload["response"]).strip()
            if "results" in payload and payload["results"]:
                first = payload["results"][0]
                if isinstance(first, dict) and "content" in first:
                    return str(first["content"]).strip()
        return ""

    # =====================================================
    # 4. FALLBACK (DEBUG ONLY)
    # =====================================================
    def _mock_response(self, prompt: str) -> str:
        return "LLM provider not configured properly."


# =====================================================
# 5. GLOBAL INSTANCE (IMPORT THIS IN RAG PIPELINE)
# =====================================================
llm = LegalLLM()


# =====================================================
# 6. EASY FUNCTION FOR RAG PIPELINE
# =====================================================
def generate_answer(query: str, context: str) -> str:
    """
    Simple wrapper for RAG pipeline
    """

    return llm.generate(query, context)