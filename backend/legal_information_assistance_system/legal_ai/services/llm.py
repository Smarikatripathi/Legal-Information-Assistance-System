def generate_answer(query, context_chunks):
    context = "\n".join(context_chunks)

    prompt = f"""
    You are a legal assistant.

    Context:
    {context}

    Question:
    {query}

    Answer clearly:
    """

    # Replace with OpenAI / Ollama / Gemini later
    return prompt