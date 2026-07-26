import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from legal_information_assistance_system.legal_ai.services.retrieval import search

print("=== TESTING CITIZENSHIP QUERY (ENGLISH) ===")
results_en = search('How to get Nepali citizenship', top_k=5)
print(f"Found {len(results_en)} results")
for i, r in enumerate(results_en):
    metadata = r.get('metadata', {})
    print(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
    print(f"   Document: {metadata.get('document_name', 'N/A')}")
    print(f"   Citation: {metadata.get('citation_label', 'N/A')}")
    print(f"   Article: {metadata.get('article', 'N/A')}")
    print(f"   Text: {r.get('text', '')[:200]}...")

print("\n\n=== TESTING CITIZENSHIP QUERY (NEPALI) ===")
results_ne = search('नेपाली नागरिकता कसरी पाउने', top_k=5)
print(f"Found {len(results_ne)} results")
for i, r in enumerate(results_ne):
    metadata = r.get('metadata', {})
    print(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
    print(f"   Document: {metadata.get('document_name', 'N/A')}")
    print(f"   Citation: {metadata.get('citation_label', 'N/A')}")
    print(f"   Article: {metadata.get('article', 'N/A')}")
    print(f"   Text: {r.get('text', '')[:200]}...")

print("\n\n=== TESTING FUNDAMENTAL RIGHTS QUERY (NEPALI) ===")
results_fr = search('नेपालको मौलिक अधिकार', top_k=5)
print(f"Found {len(results_fr)} results")
for i, r in enumerate(results_fr):
    metadata = r.get('metadata', {})
    print(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
    print(f"   Document: {metadata.get('document_name', 'N/A')}")
    print(f"   Citation: {metadata.get('citation_label', 'N/A')}")
    print(f"   Article: {metadata.get('article', 'N/A')}")
    print(f"   Text: {r.get('text', '')[:200]}...")
