import json
import os
import urllib.error
import urllib.request
from typing import Any

from legal_information_assistance_system.legal_ai.services.language import language_service


LEGAL_SYSTEM_PROMPT_TEMPLATE = """You are a Legal Information Assistant for Nepal law.

STRICT RULES:
1. Use ONLY the provided legal context — do not invent laws or interpretations.
2. If context is insufficient, say: "The provided legal sources do not contain sufficient information to answer this question."
3. Cite sources inline as [Source N] with document, part, chapter, section/article.
4. Respond ONLY in {response_language}.
5. Do not provide personal legal advice — provide legal information only.
6. Format answers in Markdown: headings (##), bullet/numbered lists, tables when useful.
7. End with a ## Sources section listing citations and links when available.
"""


class LegalLLM:
    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        ollama_host: str | None = None,
    ):
        self.provider = (provider or os.getenv("LEGAL_LLM_PROVIDER", "ollama")).lower()
        self.model = model or os.getenv("LEGAL_LLM_MODEL", "llama3.2:latest")
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_chat_endpoint = os.getenv("OLLAMA_CHAT_ENDPOINT", "/api/chat")
        # Force CPU inference when GPU CUDA kernels fail (common on Windows + older drivers).
        self.ollama_num_gpu = int(os.getenv("OLLAMA_NUM_GPU", "0"))
        
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

    def generate_from_prompt(self, full_prompt: str, *, query_language: str = "en") -> str:
        """Generate from a pre-built LangChain prompt (system + user combined)."""
        if self.provider == "openai":
            return self._openai_call(full_prompt)
        if self.provider == "ollama":
            return self._ollama_call_from_prompt(full_prompt, query_language=query_language)
        return self._mock_response()
    
    def generate_without_context(self, query: str) -> str:
        """Deprecated: grounded RAG should not call this path."""
        detected_lang = language_service.detect_language(query)
        if detected_lang == "ne":
            return "प्रदान गरिएका कानूनी स्रोतहरूमा यो प्रश्नको लागि पर्याप्त जानकारी छैन।"
        return "The provided legal sources do not contain sufficient information to answer this question."

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
            # Increased timeout to 320 seconds for complex legal analysis
            with urllib.request.urlopen(request, timeout=320) as response:
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
                f"No legal document context was retrieved.\n"
                f"Respond that the provided legal sources do not contain sufficient information.\n\n"
                f"Question: {query}"
            )
        else:
            user_content = (
                f"Here is the retrieved legal context:\n\n{context}\n\n"
                f"Question: {query}"
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": 1536,
        }
        if self.ollama_num_gpu >= 0:
            payload["options"] = {"num_gpu": self.ollama_num_gpu}
        payload["stream"] = False
        return payload

    def _ollama_call_from_prompt(self, full_prompt: str, *, query_language: str = "en") -> str:
        response_lang = self.language_names.get(query_language, "English")
        system_prompt = LEGAL_SYSTEM_PROMPT_TEMPLATE.format(response_language=response_lang)
        request_body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 1536,
        }
        if self.ollama_num_gpu >= 0:
            request_body["options"] = {"num_gpu": self.ollama_num_gpu}
        request_body["stream"] = False
        request = urllib.request.Request(
            f"{self.ollama_host}{self.ollama_chat_endpoint}",
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
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

    def _extract_ollama_response(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return ""

        # Native Ollama /api/chat response
        if "message" in payload and isinstance(payload["message"], dict):
            content = payload["message"].get("content")
            if content:
                return str(content).strip()

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
