import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def chunk_text(text, chunk_size=6):
    sentences = sent_tokenize(text)

    chunks = []
    temp = []

    for s in sentences:
        temp.append(s)

        if len(temp) >= chunk_size:
            chunks.append(" ".join(temp))
            temp = []

    if temp:
        chunks.append(" ".join(temp))

    return chunks