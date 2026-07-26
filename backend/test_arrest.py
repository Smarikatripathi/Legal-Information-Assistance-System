from legal_information_assistance_system.legal_ai.services.retrieval import search

print("=== TESTING ENGLISH QUERY ===")
results_en = search('Can the police arrest me without a warrant?', top_k=5)
print("Found " + str(len(results_en)) + " results")
for i, r in enumerate(results_en):
    metadata = r.get('metadata', {})
    print(str(i+1) + ". Score: " + str(r.get('score', 0)))
    print("   Document: " + str(metadata.get('document_name', 'N/A')))
    print("   Section: " + str(metadata.get('section', 'N/A')))
    print("   Article: " + str(metadata.get('article', 'N/A')))
    print("   Text: " + str(r.get('text', '')[:200]))

print("\n\n=== TESTING NEPALI QUERY ===")
results_ne = search('के प्रहरीले वारेन्ट बिना मलाई पक्राउ गर्न सक्छ?', top_k=5)
print("Found " + str(len(results_ne)) + " results")
for i, r in enumerate(results_ne):
    metadata = r.get('metadata', {})
    print(str(i+1) + ". Score: " + str(r.get('score', 0)))
    print("   Document: " + str(metadata.get('document_name', 'N/A')))
    print("   Section: " + str(metadata.get('section', 'N/A')))
    print("   Article: " + str(metadata.get('article', 'N/A')))
    print("   Text: " + str(r.get('text', '')[:200]))
