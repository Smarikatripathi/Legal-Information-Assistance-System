from django.test import TestCase

from legal_ai.services.hybrid_retrieval import extract_legal_numbers, hybrid_score, keyword_score
from legal_ai.services.smart_chunking import SmartLegalChunker
from legal_ai.services.text_cleaning import clean_text


class TextCleaningTests(TestCase):
    def test_removes_extra_whitespace(self):
        raw = "Section   70\n\n\nMarriage   conditions"
        cleaned = clean_text(raw)
        self.assertIn("Section 70", cleaned)
        self.assertNotIn("   ", cleaned)


class SmartChunkingTests(TestCase):
    def test_detects_section_chunks(self):
        text = (
            "Part 5\nChapter Marriage\n"
            "Section 70 Conditions of Marriage\n"
            "No marriage shall be concluded without consent.\n\n"
            "Section 71 Marriage Registration\n"
            "Every marriage must be registered."
        )
        chunks = SmartLegalChunker().chunk(text, document_name="National Civil Code")
        self.assertGreater(len(chunks), 0)
        sections = [c.get("section") for c in chunks if c.get("section")]
        self.assertTrue(any(s for s in sections))

    def test_metadata_structure(self):
        text = "Article 11 To be citizens of Nepal\nEvery person who has Nepal domicile..."
        chunks = SmartLegalChunker().chunk(text, document_name="Constitution")
        self.assertTrue(chunks)
        meta = chunks[0]["metadata"]
        self.assertIn("document_name", meta)
        self.assertIn("article", meta)


class HybridRetrievalTests(TestCase):
    def test_section_number_extraction(self):
        nums = extract_legal_numbers("What does Section 70 say about marriage?")
        self.assertIn("70", nums)

    def test_keyword_score_boosts_section_match(self):
        score = keyword_score(
            "Section 70 marriage",
            "Conditions of marriage under section 70 require consent.",
            {"section": "70", "title": "Conditions of Marriage"},
        )
        self.assertGreater(score, 0.3)

    def test_hybrid_score_combines_signals(self):
        combined = hybrid_score(
            0.8,
            "marriage section 70",
            "Section 70 sets conditions for marriage.",
            {"section": "70", "document_type": "civil_code"},
        )
        self.assertGreater(combined, 0.5)
