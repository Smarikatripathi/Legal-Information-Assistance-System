import re


class NepalLegalParser:

    def __init__(self):
        self.chunks = []
        self.current = None

    # detect legal heading using NUMBER pattern
    def is_heading(self, text):

        text = text.strip()

        patterns = [
            r"^\d+\.",        # 49.
            r"^\d+\)",        # 49)
            r"^\d+\s",        # 49 Title
            r"^[०-९]+\.",     # Nepali numbers
        ]

        return any(re.match(p, text) for p in patterns)

    def parse(self, documents):

        for doc in documents:

            text = doc["text"]
            source = doc["source"]
            page = doc["page"]

            # take first 40 chars as heading check
            snippet = text[:40]

            if self.is_heading(snippet):

                # save old block
                if self.current:
                    self.chunks.append(self.current)

                self.current = {
                    "title": snippet,
                    "content": text,
                    "source": source,
                    "pages": {page}
                }

            else:

                if self.current:
                    self.current["content"] += " " + text
                    self.current["pages"].add(page)

        # save last
        if self.current:
            self.chunks.append(self.current)

        # convert set → list
        for c in self.chunks:
            c["pages"] = list(c["pages"])

        return self.chunks 