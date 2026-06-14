import json
import os
import urllib.error
import urllib.request
from typing import Any


LEGAL_SYSTEM_PROMPT = """You are a Legal Information Assistant for Nepal law.

STRICT RULES:
1. Use ONLY the provided legal context. Never invent laws, sections, or articles.
2. Never infer legal provisions not explicitly stated in the context.
3. Never hallucinate. If the context is insufficient, say exactly:
   "The requested information could not be found in the available legal documents."
4. Always cite the source: document name, Part, Chapter, Section/Article number.
5. Explain in clear, simple language suitable for citizens and students.
6. Support both English and Nepali queries — respond in the same language as the question.
7. If multiple provisions apply, list them separately with citations.
8. Do not provide personal legal advice — provide informational summaries only.

CONTEXT FORMAT: Each block is labeled [Source N] with document and section metadata.

Answer structure:
- Direct answer first
- Legal citation (Section/Article/Part)
- Brief explanation
"""


class LegalLLM:
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

    def generate(self, query: str, context: str) -> str:
        prompt = self.build_prompt(query, context)
        if self.provider == "openai":
            return self._openai_call(prompt)
        if self.provider == "ollama":
            return self._ollama_call(prompt)
        return self._mock_response()

    def build_prompt(self, query: str, context: str) -> str:
        return (
            f"{LEGAL_SYSTEM_PROMPT}\n\n"
            f"--- LEGAL CONTEXT ---\n{context}\n\n"
            f"--- USER QUESTION ---\n{query}\n\n"
            f"--- ANSWER (with citations) ---"
        )

    def _openai_call(self, prompt: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"The requested information could not be found in the available legal documents. (LLM error: {exc})"

    def _ollama_call(self, prompt: str) -> str:
        request_body = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.ollama_host}/api/generate",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return self._extract_ollama_response(payload) or (
                "The requested information could not be found in the available legal documents."
            )
        except Exception:
            return "The requested information could not be found in the available legal documents."

    def _extract_ollama_response(self, payload: Any) -> str:
        if isinstance(payload, dict):
            if "response" in payload:
                return str(payload["response"]).strip()
        return ""

    def _mock_response(self) -> str:
        return "The requested information could not be found in the available legal documents."


llm = LegalLLM()


def generate_answer(query: str, context: str) -> str:
    return llm.generate(query, context)
