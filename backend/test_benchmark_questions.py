"""Test script to benchmark RAG system with expected questions."""

import os
import sys
import django

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from legal_information_assistance_system.legal_ai.services.rag import answer_query

# Benchmark questions from the user
benchmark_questions = [
    {
        "question": "Can a child born in Nepal to a Nepalese mother and an unknown or foreign father obtain citizenship by descent?",
        "language": "en"
    },
    {
        "question": "Are all citizens equal before the law according to the Constitution of Nepal?",
        "language": "en"
    },
    {
        "question": "Can a person who obtains Nepalese citizenship by descent get their citizenship certificate in their mother's name?",
        "language": "en"
    },
    {
        "question": "What is the legal age for marriage for both men and women under Nepalese law?",
        "language": "en"
    },
    {
        "question": "How is property divided if a person dies without a will under Nepali law?",
        "language": "en"
    },
    {
        "question": "What constitutes murder and how is it punished under Nepalese law?",
        "language": "en"
    },
    # Nepali versions
    {
        "question": "नेपालमा जम्मेको नेपाली आमाको बच्चाले वंशजका आधारमा नागरिकता पाउन सक्छ?",
        "language": "ne"
    },
    {
        "question": "नेपालको संविधानअनुसार सबै नागरिकहरू कानूनी रूपमा समान छन्?",
        "language": "ne"
    },
    {
        "question": "वंशजका आधारमा नागरिकता प्राप्त गर्ने व्यक्तले आफ्नो नागरिकता प्रमाणपत्र आमाको नाममा लिन सक्छ?",
        "language": "ne"
    },
    {
        "question": "पुरुष र महिलाको कानूनी विवाह उमेर कति हो?",
        "language": "ne"
    },
    {
        "question": "वसीयतनामा नबनाएर कसैको मृत्यु हुँदा उनको सम्पत्ति कसरी बाँडिछ?",
        "language": "ne"
    },
    {
        "question": "नेपालको कानूनअनुसार हत्या के हो र यसको सजाय कस्तो छ?",
        "language": "ne"
    }
]

def test_benchmark():
    """Test all benchmark questions."""
    print("=" * 80)
    print("BENCHMARK TESTING")
    print("=" * 80)
    
    for i, item in enumerate(benchmark_questions, 1):
        question = item["question"]
        print(f"\n{'=' * 80}")
        print(f"Question {i}/{len(benchmark_questions)}")
        print(f"{'=' * 80}")
        print(f"Question: {question}")
        print(f"Language: {item['language']}")
        print(f"{'-' * 80}")
        
        try:
            result = answer_query(question, top_k=10)
            
            print(f"Answer: {result.get('answer', 'No answer')}")
            print(f"Confidence: {result.get('confidence_score', 0.0):.2f}")
            print(f"Retrieval Time: {result.get('retrieval_time_ms', 0)}ms")
            print(f"Generation Time: {result.get('generation_time_ms', 0)}ms")
            print(f"Total Time: {result.get('response_time_ms', 0)}ms")
            print(f"Knowledge Gap Detected: {result.get('knowledge_gap_detected', False)}")
            
            if result.get('sources'):
                print(f"\nSources:")
                for j, source in enumerate(result['sources'], 1):
                    print(f"  {j}. {source.get('document', 'Unknown')} - {source.get('article', '')} {source.get('section', '')} (score: {source.get('score', 0.0):.2f})")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("BENCHMARK TESTING COMPLETE")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    test_benchmark()
