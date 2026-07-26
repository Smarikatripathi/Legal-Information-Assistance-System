from legal_information_assistance_system.legal_ai.services.retrieval import search

print("=== TESTING ENGLISH QUERY ===")
results_en = search('Can the police arrest me without a warrant?', top_k=5)
print(f"Found {len(results_en)} results")
for i, r in enumerate(results_en):
    metadata = r.get('metadata', {})
    print(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
    print(f"   Document: {metadata.get('document_name', 'N/A')}")
    print(f"   Section: {metadata.get('section', 'N/A')}")
    print(f"   Article: {metadata.get('article', 'N/A')}")
    print(f"   Text: {r.get('text', '')[:300]}...")

print("\n\n=== TESTING NEPALI QUERY ===")
results_ne = search('के प्रहरीले वारेन्ट बिना मलाई पक्राउ गर्न सक्छ?', top_k=5)
print(f"Found {len(results_ne)} results")
for i, r in enumerate(results_ne):
    metadata = r.get('metadata', {})
    print(f"\n{i+1}. Score: {r.get('score', 0):.3f}")
    print(f"   Document: {metadata.get('document_name', 'N/A')}")
    print(f"   Section: {metadata.get('section', 'N/A')}")
    print(f"   Article: {metadata.get('article', 'N/A')}")
    print(f"   Text: {r.get('text', '')[:300]}...")
