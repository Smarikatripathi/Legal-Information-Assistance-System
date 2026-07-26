from django.test import TestCase

from legal_information_assistance_system.legal_ai.services.chunking_v2 import AdvancedLegalChunker
from legal_information_assistance_system.legal_ai.services.hybrid_retrieval import (
    extract_legal_numbers,
    hybrid_score,
    keyword_score,
)
from legal_information_assistance_system.legal_ai.services.nepali_font_converter import (
    convert_legacy_to_unicode,
    is_legacy_font,
    is_unicode_text,
)
from legal_information_assistance_system.legal_ai.services.pdf_loader import (
    _is_text_based,
    is_scanned_pdf,
)
from legal_information_assistance_system.legal_ai.services.text_cleaning import clean_text

# Sample legacy Preeti text (Aviation Safety Regulation Rules).
LEGACY_PREETI_SAMPLE = "xjfO{ ;'/Iff -Joj:yf_ lgodfjnL"
LEGACY_PREETI_UNICODE = "हवाई सरक्षा (व्यवस्था) नियमावली"


class TextCleaningTests(TestCase):
    def test_removes_extra_whitespace(self):
        raw = "Section   70\n\n\nMarriage   conditions"
        cleaned = clean_text(raw)
        self.assertIn("Section 70", cleaned)
        self.assertNotIn("   ", cleaned)


class NepaliFontConverterTests(TestCase):
    def test_detects_unicode_nepali(self):
        text = "यो कानून धारा १ र ऐन सम्बन्धी हो।"
        self.assertTrue(is_unicode_text(text))
        self.assertFalse(is_legacy_font(text))

    def test_detects_legacy_preeti_text(self):
        self.assertFalse(is_unicode_text(LEGACY_PREETI_SAMPLE))
        self.assertTrue(is_legacy_font(LEGACY_PREETI_SAMPLE))

    def test_converts_legacy_preeti_to_unicode(self):
        converted = convert_legacy_to_unicode(LEGACY_PREETI_SAMPLE)
        self.assertTrue(is_unicode_text(converted))
        self.assertIn("हवाई", converted)
        self.assertIn("नियमावली", converted)

    def test_unicode_text_is_not_reconverted(self):
        text = "नेपालको संविधान"
        self.assertEqual(convert_legacy_to_unicode(text), text)


class PdfExtractionTests(TestCase):
    def test_treats_nepali_legal_text_with_markers_as_text_based(self):
        pages = ["This legal text discusses धारा १ and ऐन in the context of citizenship."]
        self.assertTrue(_is_text_based(pages))

    def test_treats_converted_legacy_text_as_text_based(self):
        converted = convert_legacy_to_unicode(LEGACY_PREETI_SAMPLE)
        self.assertTrue(_is_text_based([converted]))

    def test_legacy_text_not_classified_as_scanned(self):
        pages = [LEGACY_PREETI_SAMPLE]
        self.assertFalse(is_scanned_pdf("nonexistent.pdf", pages))

    def test_unicode_text_not_classified_as_scanned(self):
        pages = [LEGACY_PREETI_UNICODE]
        self.assertFalse(is_scanned_pdf("nonexistent.pdf", pages))


class AdvancedChunkingTests(TestCase):
    def test_detects_section_chunks(self):
        text = (
            "Part 5\nChapter Marriage\n"
            "Section 70 Conditions of Marriage\n"
            "No marriage shall be concluded without consent.\n\n"
            "Section 71 Marriage Registration\n"
            "Every marriage must be registered."
        )
        chunker = AdvancedLegalChunker(document_id=1, document_name="National Civil Code", document_type="act")
        chunks = chunker.chunk(text)
        self.assertGreater(len(chunks), 0)
        sections = [c.section_number for c in chunks if c.section_number]
        self.assertTrue(any(s for s in sections))

    def test_metadata_structure(self):
        text = "Article 11 To be citizens of Nepal\nEvery person who has Nepal domicile..."
        chunker = AdvancedLegalChunker(document_id=1, document_name="Constitution", document_type="constitution")
        chunks = chunker.chunk(text)
        self.assertTrue(chunks)
        meta = chunks[0]
        self.assertEqual(meta.document_name, "Constitution")
        self.assertIsNotNone(meta.article_number)


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
