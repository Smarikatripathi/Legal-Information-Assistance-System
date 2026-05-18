import os
from typing import Optional


# =====================================================
# 1. BASE LLM CLASS
# =====================================================
class LegalLLM:
    """
    10/10 LLM wrapper for Legal RAG system
    """

    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()

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

        return f"""
You are a highly accurate LEGAL ASSISTANT AI for Nepal law system.

RULES:
- Use ONLY the provided context
- Do NOT hallucinate or assume extra laws
- If context is insufficient, say "Not enough legal information in documents"
- Keep answer simple and legally correct
- Cite reasoning from context

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    # =====================================================
    # 2. OPENAI IMPLEMENTATION
    # =====================================================
    def _openai_call(self, prompt: str) -> str:
        """
        OpenAI GPT call (GPT-4 / GPT-3.5)
        """

        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal assistant AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2  # IMPORTANT for legal accuracy
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"OpenAI Error: {str(e)}"

    # =====================================================
    # 3. OLLAMA LOCAL LLM (FREE OPTION)
    # =====================================================
    def _ollama_call(self, prompt: str) -> str:
        """
        Local LLM using Ollama (Llama3 / Mistral)
        """

        try:
            import requests

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )

            return response.json().get("response", "")

        except Exception as e:
            return f"Ollama Error: {str(e)}"

    # =====================================================
    # 4. FALLBACK (DEBUG ONLY)
    # =====================================================
    def _mock_response(self, prompt: str) -> str:
        return "LLM provider not configured properly."


# =====================================================
# 5. GLOBAL INSTANCE (IMPORT THIS IN RAG PIPELINE)
# =====================================================
llm = LegalLLM(provider="openai")  # change to "ollama" if needed


# =====================================================
# 6. EASY FUNCTION FOR RAG PIPELINE
# =====================================================
def generate_answer(query: str, context: str) -> str:
    """
    Simple wrapper for RAG pipeline
    """

    return llm.generate(query, context)