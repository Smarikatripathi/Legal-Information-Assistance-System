from django.core.management.base import BaseCommand

from legal_information_assistance_system.legal_ai.services.retrieval import search


class Command(BaseCommand):
    help = "Test retrieval for citizenship and fundamental rights queries"

    def handle(self, *args, **options):
        self.stdout.write("=== TESTING CITIZENSHIP QUERY (ENGLISH) ===")
        results_en = search('How to get Nepali citizenship', top_k=5)
        self.stdout.write(f"Found {len(results_en)} results")
        for i, r in enumerate(results_en):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")

        self.stdout.write("\n\n=== TESTING CITIZENSHIP QUERY (NEPALI) ===")
        results_ne = search('नेपाली नागरिकता कसरी पाउने', top_k=5)
        self.stdout.write(f"Found {len(results_ne)} results")
        for i, r in enumerate(results_ne):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")

        self.stdout.write("\n\n=== TESTING FUNDAMENTAL RIGHTS QUERY (NEPALI) ===")
        results_fr = search('नेपालको मौलिक अधिकार', top_k=5)
        self.stdout.write(f"Found {len(results_fr)} results")
        for i, r in enumerate(results_fr):
            metadata = r.get('metadata', {})
            self.stdout.write(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
            self.stdout.write(f"   Document: {metadata.get('document_name', 'N/A')}")
            self.stdout.write(f"   Citation: {metadata.get('citation_label', 'N/A')}")
            self.stdout.write(f"   Article: {metadata.get('article', 'N/A')}")
            self.stdout.write(f"   Text: {r.get('text', '')[:200]}...")
