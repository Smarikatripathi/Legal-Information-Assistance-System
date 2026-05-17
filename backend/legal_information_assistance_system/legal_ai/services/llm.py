import ollama


def generate_answer(query, context_chunks):

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a Nepali legal assistant.

Use ONLY provided legal context.

Context:
{context}

Question:
{query}

Answer clearly.
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]