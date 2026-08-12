from django.test import TestCase
from unittest.mock import patch, MagicMock

from legal_information_assistance_system.legal_ai.services.rag import answer_query
from legal_information_assistance_system.legal_ai.models import AdminNotification, KnowledgeGap, LegalDocument, LegalChunk


class KnowledgeGapDetectionTests(TestCase):
    def setUp(self):
        self.doc = LegalDocument.objects.create(
            title="Test Document",
            document_type="act",
        )
        LegalChunk.objects.create(
            doc=self.doc,
            text="Dummy chunk text for retrieval placeholder.",
        )
    @patch('legal_information_assistance_system.legal_ai.services.rag.search')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate_from_prompt')
    def test_land_ownership_question_no_gap(self, mock_generate_from_prompt, mock_generate, mock_search):
        query = "How do I register land ownership in Nepal?"
        mock_search.return_value = [
            {
                "text": "Article 147: Land registration shall follow the procedures prescribed by law.",
                "score": 0.85,
                "metadata": {"document_name": "Muluki Ain", "article": "147"},
            }
        ]
        mock_generate.return_value = "<BACKEND_NOTIFICATION>\n{\n  \"knowledge_gap\": false\n}\n</BACKEND_NOTIFICATION>\n\n## Direct Answer\nAccording to Article 147, land registration follows the prescribed procedure."
        mock_generate_from_prompt.return_value = '{"is_answerable": true, "knowledge_gap": false, "reason": "The context is sufficient."}'

        response = answer_query(query, top_k=1)

        self.assertFalse(response.get('knowledge_gap_detected'))
        self.assertEqual(KnowledgeGap.objects.count(), 0)
        self.assertEqual(AdminNotification.objects.count(), 0)

    @patch('legal_information_assistance_system.legal_ai.services.rag.search')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate_from_prompt')
    def test_relevant_document_no_notification_when_llm_marks_gap(self, mock_generate_from_prompt, mock_generate, mock_search):
        query = "What is the legal right to education in Article 31?"
        mock_search.return_value = [
            {
                "text": "Article 31: Every Nepalese community residing in Nepal shall have the right to get education in its mother tongue and, for that purpose, to open and operate schools and educational institutes, in accordance with law.",
                "score": 0.90,
                "metadata": {"document_name": "Constitution", "article": "31"},
            }
        ]
        mock_generate.return_value = "<BACKEND_NOTIFICATION>\n{\n  \"knowledge_gap\": true\n}\n</BACKEND_NOTIFICATION>\n\n## Direct Answer\nThe Constitution guarantees the right to education in one's mother tongue."
        mock_generate_from_prompt.return_value = '{"is_answerable": true, "knowledge_gap": false, "reason": "The context is sufficient."}'

        response = answer_query(query, top_k=1)

        self.assertFalse(response.get('knowledge_gap_detected'))
        self.assertEqual(KnowledgeGap.objects.count(), 0)
        self.assertEqual(AdminNotification.objects.count(), 0)

    @patch('legal_information_assistance_system.legal_ai.services.rag.search')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate')
    @patch('legal_information_assistance_system.legal_ai.services.rag.llm.generate_from_prompt')
    def test_president_name_question_gap(self, mock_generate_from_prompt, mock_generate, mock_search):
        query = "What is the name of president of Nepal?"
        mock_search.return_value = [
            {
                "text": "Article 61: The President shall promote national unity and perform duties as assigned.",
                "score": 0.80,
                "metadata": {"document_name": "Constitution", "article": "61"},
            }
        ]
        mock_generate.return_value = "<BACKEND_NOTIFICATION>\n{\n  \"knowledge_gap\": true\n}\n</BACKEND_NOTIFICATION>\n\n## Direct Answer\nThe retrieved documents describe the President's role, but do not provide the current President's name."
        mock_generate_from_prompt.return_value = '{"is_answerable": false, "knowledge_gap": true, "reason": "The retrieved context discusses the President but does not contain the current President\'s name."}'

        response = answer_query(query, top_k=1)

        self.assertTrue(response.get('knowledge_gap_detected'))
        self.assertEqual(KnowledgeGap.objects.count(), 1)
        self.assertEqual(AdminNotification.objects.count(), 1)
