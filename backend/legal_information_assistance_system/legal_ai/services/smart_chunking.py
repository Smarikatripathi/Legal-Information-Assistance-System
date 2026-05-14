import re

def smart_chunk(text, max_chunk_size=800):
    """
    Legal PDF smart chunking without headings
    (works for numbered constitution like Nepal)
    """

    # Step 1: Normalize text
    text = re.sub(r'\n+', '\n', text)  # remove extra new lines
    text = text.strip()

    # Step 2: Split by numbers (main logic)
    # This detects lines that are only numbers
    parts = re.split(r'\n\s*\d+\s*\n', text)

    chunks = []
    current_chunk = ""

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # If chunk becomes too big, split it
        if len(current_chunk) + len(part) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = part
        else:
            current_chunk += "\n" + part

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks