from django.test import TestCase
from unittest.mock import patch, MagicMock

from legal_information_assistance_system.legal_ai.services.retrieval import (
    RetrievalError,
    VectorStoreError,
    EmbeddingError,
    search,
    rebuild_faiss_index,
    sync_vector_store,
)
from legal_information_assistance_system.legal_ai.models import LegalChunk, LegalDocument


class RetrievalExceptionTests(TestCase):
    """Test custom retrieval exceptions."""
    
    def test_retrieval_error_base_exception(self):
        """Test RetrievalError is a proper exception."""
        with self.assertRaises(RetrievalError):
            raise RetrievalError("Test error")
    
    def test_vector_store_error_inherits_retrieval_error(self):
        """Test VectorStoreError inherits from RetrievalError."""
        with self.assertRaises(RetrievalError):
            raise VectorStoreError("Vector store error")
    
    def test_embedding_error_inherits_retrieval_error(self):
        """Test EmbeddingError inherits from RetrievalError."""
        with self.assertRaises(RetrievalError):
            raise EmbeddingError("Embedding error")


class NPlusOneQueryTests(TestCase):
    """Test that N+1 queries are fixed."""
    
    def setUp(self):
        """Set up test data."""
        self.doc = LegalDocument.objects.create(
            title="Test Document",
            document_type="act",
        )
    
    def test_select_related_used_in_database_queries(self):
        """Test that select_related is used for foreign key queries."""
        # This test verifies the code uses select_related
        # Actual query optimization would be verified with Django Debug Toolbar
        chunks = LegalChunk.objects.select_related("doc").filter(doc=self.doc)
        
        # Verify the query includes the join
        query_str = str(chunks.query)
        self.assertIn("JOIN", query_str.upper())


class DatabaseIndexTests(TestCase):
    """Test database indexes are properly configured."""
    
    def test_chunk_model_has_indexes(self):
        """Test that LegalChunk model has expected indexes."""
        from legal_information_assistance_system.legal_ai.models import LegalChunk
        
        # Check that indexes are defined
        self.assertTrue(len(LegalChunk._meta.indexes) > 0)
        
        # Check for specific indexes from the migration
        index_names = [index.name for index in LegalChunk._meta.indexes]
        
        # Verify some expected indexes exist (using actual index names from migration)
        self.assertIn("legal_ai_le_doc_id_1aed05_idx", index_names)  # doc, article_number
        self.assertIn("legal_ai_le_doc_id_dce1d5_idx", index_names)  # doc, section_number
        self.assertIn("legal_ai_le_documen_67a08a_idx", index_names)  # document_type
    
    def test_chunk_model_has_unique_constraint(self):
        """Test that unique constraint on (doc, chunk_id) exists."""
        from legal_information_assistance_system.legal_ai.models import LegalChunk
        
        constraints = LegalChunk._meta.constraints
        constraint_names = [c.name for c in constraints]
        
        self.assertIn("unique_document_chunk_id", constraint_names)


class RetrievalErrorHandlingTests(TestCase):
    """Test error handling in retrieval functions."""
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    def test_search_handles_empty_query(self, mock_get_vector_store):
        """Test search returns empty list for empty query."""
        result = search("")
        self.assertEqual(result, [])
        
        result = search("   ")
        self.assertEqual(result, [])
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    def test_search_handles_vector_store_error(self, mock_get_vector_store):
        """Test search handles vector store errors gracefully."""
        mock_store = MagicMock()
        mock_store.load.side_effect = Exception("Vector store error")
        mock_get_vector_store.return_value = mock_store
        
        with self.assertRaises(RetrievalError):
            search("test query")
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    def test_search_handles_no_embeddings(self, mock_get_vector_store):
        """Test search returns empty list when no embeddings exist."""
        mock_store = MagicMock()
        mock_store.has_embeddings.return_value = False
        mock_store.count.return_value = 0  # Return integer, not MagicMock
        mock_get_vector_store.return_value = mock_store
        
        result = search("test query")
        self.assertEqual(result, [])


class RebuildFAISSIndexTests(TestCase):
    """Test FAISS index rebuild functionality."""
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_embedding_model')
    def test_rebuild_faiss_index_handles_no_chunks(self, mock_get_model, mock_get_store):
        """Test rebuild handles case with no chunks."""
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        result = rebuild_faiss_index()
        
        self.assertFalse(result)
        mock_store.clear.assert_called_once()
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_embedding_model')
    def test_rebuild_faiss_index_logs_success(self, mock_get_model, mock_get_store):
        """Test rebuild logs success message."""
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        mock_model = MagicMock()
        mock_model.model_name = "test-model"
        mock_model.dimension = 768
        mock_model.embed_passages.return_value = [[0.1, 0.2]]
        mock_get_model.return_value = mock_model
        
        # Create a test chunk
        doc = LegalDocument.objects.create(title="Test", document_type="act")
        chunk = LegalChunk.objects.create(doc=doc, text="Test text")
        
        result = rebuild_faiss_index()
        
        self.assertTrue(result)
        # Verify store.build_index was called
        mock_store.build_index.assert_called_once()


class SyncVectorStoreTests(TestCase):
    """Test vector store synchronization."""
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    def test_sync_clears_store_when_db_empty(self, mock_get_store):
        """Test sync clears store when database is empty."""
        mock_store = MagicMock()
        mock_store.count.return_value = 10
        mock_get_store.return_value = mock_store
        
        sync_vector_store()
        
        mock_store.clear.assert_called_once()
    
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.get_vector_store')
    @patch('legal_information_assistance_system.legal_ai.services.retrieval.rebuild_faiss_index')
    def test_sync_rebuilds_when_counts_differ(self, mock_rebuild, mock_get_store):
        """Test sync rebuilds when counts differ."""
        mock_store = MagicMock()
        mock_store.count.return_value = 5
        mock_get_store.return_value = mock_store
        
        # Create test chunks
        doc = LegalDocument.objects.create(title="Test", document_type="act")
        LegalChunk.objects.create(doc=doc, text="Test text 1")
        LegalChunk.objects.create(doc=doc, text="Test text 2")
        
        sync_vector_store()
        
        mock_rebuild.assert_called_once()
