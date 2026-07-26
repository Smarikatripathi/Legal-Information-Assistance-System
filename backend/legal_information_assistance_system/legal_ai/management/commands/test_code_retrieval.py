from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.services.retrieval import search


class Command(BaseCommand):
    help = "Test retrieval for Civil and Criminal Code queries"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTING CIVIL CODE QUERY (NEPALI) ===")
        results_civil = search('मुलुकी देवानी संहिता अनुसार अनुबन्ध', top_k=5)
        self.stdout.write(f"Found {len(results_civil)} results")
        for i, r in enumerate(results_civil):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")

        self.stdout.write("\n\n=== TESTING CRIMINAL CODE QUERY (NEPALI) ===")
        results_criminal = search('मुलुकी अपराध संहिता अनुसार चोरी', top_k=5)
        self.stdout.write(f"Found {len(results_criminal)} results")
        for i, r in enumerate(results_criminal):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")

        self.stdout.write("\n\n=== TESTING CIVIL CODE QUERY (ENGLISH) ===")
        results_civil_en = search('Civil Code contract law', top_k=5)
        self.stdout.write(f"Found {len(results_civil_en)} results")
        for i, r in enumerate(results_civil_en):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")
