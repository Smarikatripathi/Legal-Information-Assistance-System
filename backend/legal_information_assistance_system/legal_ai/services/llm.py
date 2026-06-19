import json
import os
import urllib.error
import urllib.request
from typing import Any

from legal_ai.services.language import language_service


LEGAL_SYSTEM_PROMPT_TEMPLATE = """You are a Legal Information Assistant for Nepal law.

GUIDELINES:
1. Use the provided legal context as primary source when available.
2. You MAY infer related legal provisions and principles from the context.
3. You MAY draw logical conclusions from stated laws (e.g., rights granted, duties imposed).
4. Always cite sources when available: document name, Part, Chapter, Section/Article number.
5. Explain in clear, simple language suitable for citizens and students.
6. **IMPORTANT: Respond ONLY in {response_language}. The user asked in {response_language}, so answer in {response_language} only.**
7. If multiple provisions apply, list them separately with citations.
8. Do not provide personal legal advice — provide informational summaries only.
9. NEVER say "information not found" — instead explain what you DO know and limitations.
10. Use reasoning to answer constitutional and legal questions, even if context is partial.

CONTEXT FORMAT: Each block is labeled [Source N] with document and section metadata.

Answer structure:
- Direct answer first (based on law + reasoning)
- Legal citations (if available)
- Brief explanation
- Limitations (if applicable)
"""


class LegalLLM:
    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        ollama_host: str | None = None,
    ):
        self.provider = (provider or os.getenv("LEGAL_LLM_PROVIDER", "ollama")).lower()
        self.model = model or os.getenv("LEGAL_LLM_MODEL", "llama3:latest")
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_chat_endpoint = os.getenv("OLLAMA_CHAT_ENDPOINT", "/v1/chat/completions")
        
        # Language mappings
        self.language_names = {
            "en": "English",
            "ne": "Nepali",
        }

    def generate(self, query: str, context: str) -> str:
        if self.provider == "openai":
            prompt = self.build_prompt(query, context)
            return self._openai_call(prompt)
        if self.provider == "ollama":
            return self._ollama_call(query, context)
        return self._mock_response()
    
    def generate_without_context(self, query: str) -> str:
        """Fallback: answer legal questions without retrieval context using reasoning."""
        detected_lang = language_service.detect_language(query)
        response_lang = self.language_names.get(detected_lang, "English")
        
        if self.provider == "openai":
            fallback_prompt = (
                f"You are a Legal Information Assistant for Nepal law.\n"
                f"Respond in {response_lang} only.\n\n"
                f"The user is asking about Nepal law, but no specific legal document context is available.\n"
                f"Based on your knowledge of Nepal's Constitution, Civil Code, and Criminal Code, provide the best answer you can.\n"
                f"If you don't know the answer, be honest about the limitations.\n\n"
                f"Question: {query}\n\n"
                f"Answer:"
            )
            return self._openai_call(fallback_prompt)
        if self.provider == "ollama":
            return self._ollama_call(query, context=None, fallback=True)
        return "I don't have enough information to answer this question about Nepal law."

    def build_prompt(self, query: str, context: str) -> str:
        # Detect query language
        detected_lang = language_service.detect_language(query)
        response_lang = self.language_names.get(detected_lang, "English")
        
        system_prompt = LEGAL_SYSTEM_PROMPT_TEMPLATE.format(response_language=response_lang)
        
        return (
            f"{system_prompt}\n\n"
            f"--- LEGAL CONTEXT ---\n{context}\n\n"
            f"--- USER QUESTION (in {response_lang}) ---\n{query}\n\n"
            f"--- ANSWER (MUST be in {response_lang} only) ---"
        )

    def _openai_call(self, prompt: str) -> str:
        try:
            import importlib
            openai = importlib.import_module("openai")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "OpenAI SDK is not installed. Install it with `pip install openai` "
                "or set LEGAL_LLM_PROVIDER to 'ollama'."
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure the environment variable "
                "or switch LEGAL_LLM_PROVIDER to 'ollama'."
            )

        try:
            client = openai.OpenAI(api_key=api_key)

            detected_lang = language_service.detect_language(prompt) if "USER QUESTION (in" in prompt else "en"
            response_lang = self.language_names.get(detected_lang, "English")
            system_prompt = LEGAL_SYSTEM_PROMPT_TEMPLATE.format(response_language=response_lang)

            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"OpenAI call failed: {exc}") from exc

    def _ollama_call(self, query: str, context: str | None = None, fallback: bool = False) -> str:
        request_body = self._build_ollama_chat_payload(query, context=context, fallback=fallback)
        request = urllib.request.Request(
            f"{self.ollama_host}{self.ollama_chat_endpoint}",
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            # Increased timeout to 120 seconds for complex legal analysis
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))

            response_text = self._extract_ollama_response(payload)
            if response_text:
                return response_text
            raise RuntimeError("Ollama responded without valid text")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Ollama call failed ({exc.code}): {exc.reason}. Response body: {body}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama call failed: {exc}") from exc

    def _build_ollama_chat_payload(self, query: str, context: str | None = None, fallback: bool = False) -> dict[str, Any]:
        detected_lang = language_service.detect_language(query)
        response_lang = self.language_names.get(detected_lang, "English")
        system_prompt = LEGAL_SYSTEM_PROMPT_TEMPLATE.format(response_language=response_lang)

        if fallback or not context:
            user_content = (
                f"The user is asking about Nepal law, but no specific legal document context is available.\n"
                f"Based on your knowledge of Nepal's Constitution, Civil Code, and Criminal Code, provide the best answer you can.\n"
                f"If you don't know the answer, be honest about the limitations.\n\n"
                f"Question: {query}"
            )
        else:
            user_content = (
                f"Here is the retrieved legal context:\n\n{context}\n\n"
                f"Question: {query}"
            )

        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
        }

    def _extract_ollama_response(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return ""

        # OpenAI-style chat completion response
        if "choices" in payload and isinstance(payload["choices"], list) and payload["choices"]:
            first = payload["choices"][0]
            if isinstance(first, dict):
                if "message" in first and isinstance(first["message"], dict):
                    content = first["message"].get("content")
                    if content:
                        return str(content).strip()
                if "text" in first and first["text"]:
                    return str(first["text"]).strip()

        if "response" in payload and payload["response"]:
            return str(payload["response"]).strip()

        if "results" in payload and isinstance(payload["results"], list) and payload["results"]:
            first = payload["results"][0]
            if isinstance(first, dict):
                if "content" in first and first["content"]:
                    return str(first["content"]).strip()
                if "response" in first and first["response"]:
                    return str(first["response"]).strip()

        if "output" in payload:
            output = payload["output"]
            if isinstance(output, str) and output:
                return output.strip()
            if isinstance(output, list) and output:
                return "\n".join(str(item).strip() for item in output if item)

        return ""

    def _mock_response(self) -> str:
        return "LLM provider is not configured or is unavailable."


llm = LegalLLM()


def generate_answer(query: str, context: str) -> str:
    return llm.generate(query, context)
