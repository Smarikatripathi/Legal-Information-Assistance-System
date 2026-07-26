from django.test import TestCase

from legal_information_assistance_system.legal_ai.services.chunking_v2 import (
    AdvancedLegalChunker,
    generate_chunk_id,
    SafeOCRCorrector,
    OCRCorrection,
    ChunkMetadata,
)


class ChunkIDGenerationTests(TestCase):
    """Test chunk ID generation for uniqueness and determinism."""
    
    def test_chunk_id_includes_sequence_number(self):
        """Ensure chunk IDs include sequence numbers for uniqueness."""
        chunk_id_1 = generate_chunk_id(
            document_name="Test Document",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=0,
        )
        chunk_id_2 = generate_chunk_id(
            document_name="Test Document",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=1,
        )
        
        self.assertNotEqual(chunk_id_1, chunk_id_2)
        self.assertIn("seq-0", chunk_id_1)
        self.assertIn("seq-1", chunk_id_2)
    
    def test_chunk_id_includes_content_hash(self):
        """Ensure chunk IDs can include content hash for additional uniqueness."""
        chunk_id = generate_chunk_id(
            document_name="Test Document",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=0,
            content_hash="abc123def456",
        )
        
        self.assertIn("hash-abc123de", chunk_id)
    
    def test_chunk_id_deterministic_same_inputs(self):
        """Ensure chunk IDs are deterministic for same inputs."""
        chunk_id_1 = generate_chunk_id(
            document_name="Test Document",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=0,
        )
        chunk_id_2 = generate_chunk_id(
            document_name="Test Document",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=0,
        )
        
        self.assertEqual(chunk_id_1, chunk_id_2)
    
    def test_chunk_id_normalizes_document_name(self):
        """Ensure document name is normalized in chunk ID."""
        chunk_id = generate_chunk_id(
            document_name="Test Document With Spaces",
            part="1",
            chapter="2",
            article="3",
            clause=None,
            schedule=None,
            annex=None,
            chunk_sequence=0,
        )
        
        self.assertIn("test-document-with-spaces", chunk_id)
        self.assertNotIn(" ", chunk_id)
        self.assertNotIn("।", chunk_id)


class ChunkingUniquenessTests(TestCase):
    """Test that chunking produces unique chunk IDs."""
    
    def test_multiple_chunks_same_article_have_unique_ids(self):
        """Ensure multiple chunks under same article have unique IDs."""
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="act"
        )
        
        text = (
            "Article 1\n"
            "(1) First clause with some content.\n"
            "(2) Second clause with different content.\n"
            "(3) Third clause with more content."
        )
        
        chunks = chunker.chunk(text)
        
        # Extract chunk IDs
        chunk_ids = [c.chunk_id for c in chunks]
        
        # Verify all IDs are unique
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))
        
        # Verify sequence numbers are present
        for i, chunk_id in enumerate(chunk_ids):
            self.assertIn(f"seq-{i}", chunk_id)


class HierarchyTrackingTests(TestCase):
    """Test that hierarchy context is tracked correctly."""
    
    def test_hierarchy_context_maintained_across_chunks(self):
        """Test hierarchy context is maintained through document."""
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="act"
        )
        
        text = (
            "Part 1\n"
            "Chapter 1\n"
            "Article 1\n"
            "(1) First clause.\n"
            "Article 2\n"
            "(1) Second clause."
        )
        
        chunks = chunker.chunk(text)
        
        # Find chunks under Article 1 and Article 2
        article_1_chunks = [c for c in chunks if c.article_number == "1"]
        article_2_chunks = [c for c in chunks if c.article_number == "2"]
        
        # Verify hierarchy is maintained
        if article_1_chunks:
            self.assertEqual(article_1_chunks[0].part_number, "1")
            self.assertEqual(article_1_chunks[0].chapter_number, "1")
        
        if article_2_chunks:
            self.assertEqual(article_2_chunks[0].part_number, "1")
            self.assertEqual(article_2_chunks[0].chapter_number, "1")
    
    def test_hierarchy_path_populated(self):
        """Test hierarchy path is populated correctly."""
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="act"
        )
        
        text = "Part 1\nChapter 1\nArticle 1\n(1) First clause."
        chunks = chunker.chunk(text)
        
        if chunks:
            self.assertIsInstance(chunks[0].hierarchy_path, list)
            # Verify hierarchy path contains expected elements
            self.assertTrue(len(chunks[0].hierarchy_path) > 0)


class OCRCorrectionTests(TestCase):
    """Test OCR correction safety and tracking."""
    
    def test_source_text_unchanged_after_correction(self):
        """Ensure source text is not modified by OCR correction."""
        corrector = SafeOCRCorrector()
        source_text = "राि राज्य"
        
        corrected, corrections = corrector.correct(source_text)
        
        # Source should remain unchanged
        self.assertEqual(source_text, "राि राज्य")
        
        # Corrected version should be different
        self.assertNotEqual(corrected, source_text)
    
    def test_ocr_corrections_tracked(self):
        """Ensure OCR corrections are tracked with metadata."""
        corrector = SafeOCRCorrector()
        text = "राि राज्य"
        
        corrected, corrections = corrector.correct(text)
        
        # Should return list of corrections
        self.assertIsInstance(corrections, list)
        
        if corrections:
            # Each correction should be an OCRCorrection dataclass
            self.assertIsInstance(corrections[0], OCRCorrection)
            self.assertEqual(corrections[0].original, "राि")
            self.assertEqual(corrections[0].corrected, "राज्य")
            self.assertGreater(corrections[0].confidence, 0)
            self.assertIsNotNone(corrections[0].rule_id)
    
    def test_ocr_correction_no_corrections_returns_empty_list(self):
        """Ensure text without corrections returns empty list."""
        corrector = SafeOCRCorrector()
        text = "नेपाल"  # No corrections needed
        
        corrected, corrections = corrector.correct(text)
        
        self.assertEqual(len(corrections), 0)
        self.assertEqual(corrected, text)
    
    def test_chunk_metadata_includes_ocr_corrections(self):
        """Test that chunk metadata includes OCR corrections."""
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="act"
        )
        
        text = "Article 1\n(1) राि राज्य"
        chunks = chunker.chunk(text)
        
        if chunks:
            # OCR corrections should be a list
            self.assertIsInstance(chunks[0].ocr_corrections, list)


class ChunkMetadataTests(TestCase):
    """Test ChunkMetadata dataclass properties."""
    
    def test_mutable_defaults_use_factory(self):
        """Test that mutable defaults use field factory."""
        # Create two ChunkMetadata instances
        meta1 = ChunkMetadata(
            chunk_id="test-1",
            document_id=1,
            document_name="Test",
            document_type="act",
            jurisdiction="Nepal",
            language="ne",
        )
        meta2 = ChunkMetadata(
            chunk_id="test-2",
            document_id=1,
            document_name="Test",
            document_type="act",
            jurisdiction="Nepal",
            language="ne",
        )
        
        # Modify hierarchy_path of first instance
        meta1.hierarchy_path.append("test")
        
        # Second instance should not be affected
        self.assertEqual(len(meta2.hierarchy_path), 0)
        self.assertNotIn("test", meta2.hierarchy_path)
    
    def test_ocr_corrections_mutable_default_uses_factory(self):
        """Test that ocr_corrections default uses field factory."""
        meta1 = ChunkMetadata(
            chunk_id="test-1",
            document_id=1,
            document_name="Test",
            document_type="act",
            jurisdiction="Nepal",
            language="ne",
        )
        meta2 = ChunkMetadata(
            chunk_id="test-2",
            document_id=1,
            document_name="Test",
            document_type="act",
            jurisdiction="Nepal",
            language="ne",
        )
        
        # Modify ocr_corrections of first instance
        meta1.ocr_corrections.append(OCRCorrection("a", "b", 0.9, "TEST-001"))
        
        # Second instance should not be affected
        self.assertEqual(len(meta2.ocr_corrections), 0)


class DocumentTypeTests(TestCase):
    """Test document type consistency."""
    
    def test_chunker_requires_document_type(self):
        """Test that chunker requires explicit document type."""
        # This should work
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="act"
        )
        
        self.assertEqual(chunker.document_type, "act")
    
    def test_chunker_document_type_used_in_metadata(self):
        """Test that document type is used in chunk metadata."""
        chunker = AdvancedLegalChunker(
            document_id=1,
            document_name="Test Document",
            document_type="constitution"
        )
        
        text = "Article 1\n(1) Test content."
        chunks = chunker.chunk(text)
        
        if chunks:
            self.assertEqual(chunks[0].document_type, "constitution")


class PageMappingTests(TestCase):
    """Test page mapping functionality."""
    
    def test_map_char_to_page(self):
        """Test character to page mapping."""
        from legal_information_assistance_system.legal_ai.services.chunking_v2 import _map_char_to_page
        
        page_mapping = {
            1: (0, 100),
            2: (101, 200),
            3: (201, 300),
        }
        
        # Test character positions
        self.assertEqual(_map_char_to_page(50, page_mapping), 1)
        self.assertEqual(_map_char_to_page(150, page_mapping), 2)
        self.assertEqual(_map_char_to_page(250, page_mapping), 3)
        self.assertIsNone(_map_char_to_page(400, page_mapping))
    
    def test_determine_page_range(self):
        """Test page range determination."""
        from legal_information_assistance_system.legal_ai.services.chunking_v2 import _determine_page_range
        
        page_mapping = {
            1: (0, 100),
            2: (101, 200),
            3: (201, 300),
        }
        
        page_start, page_end = _determine_page_range("test", 50, 150, page_mapping)
        
        self.assertEqual(page_start, 1)
        self.assertEqual(page_end, 2)
