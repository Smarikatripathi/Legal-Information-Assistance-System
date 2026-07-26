"""
Legal QA Test Runner
Execute end-to-end tests for the Legal Information Assistance System
"""

import os
import sys
import django
import time
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from legal_information_assistance_system.legal_ai.services.rag_pipeline import answer_query
from legal_information_assistance_system.legal_ai.services.domain_classifier import classify_query
from legal_information_assistance_system.legal_ai.services.llm import correct_typos
from test_suite import TEST_SUITE, CRITICAL_TESTS


class TestResult:
    def __init__(self, test_id, question, category):
        self.test_id = test_id
        self.question = question
        self.category = category
        self.start_time = None
        self.end_time = None
        self.response = None
        self.response_time_ms = None
        self.error = None
        self.evaluation = None
        
    def to_dict(self):
        return {
            'test_id': self.test_id,
            'question': self.question,
            'category': self.category,
            'response_time_ms': self.response_time_ms,
            'response': self.response,
            'error': str(self.error) if self.error else None,
            'evaluation': self.evaluation,
        }


def run_test(question, test_id, category):
    """Run a single test question through the RAG pipeline."""
    result = TestResult(test_id, question, category)
    
    try:
        # Apply typo correction
        corrected_query = correct_typos(question)
        
        # Domain classification
        classification = classify_query(question)
        
        result.start_time = time.time()
        
        # Run through RAG pipeline
        response = answer_query(
            corrected_query,
            top_k=5,
            conversation_id=None,
            user_id=None,
            use_enhanced=True,
        )
        
        result.end_time = time.time()
        result.response_time_ms = (result.end_time - result.start_time) * 1000
        result.response = response
        
        # Add classification info
        result.response['classification'] = {
            'is_legal': classification.is_legal,
            'reason': classification.reason,
            'language': classification.language,
        }
        
    except Exception as e:
        result.error = e
        result.end_time = time.time()
        result.response_time_ms = (result.end_time - result.start_time) * 1000 if result.start_time else None
    
    return result


def evaluate_result(result, expected_behavior, expected_documents):
    """Evaluate a test result against expected behavior."""
    evaluation = {
        'status': 'UNKNOWN',
        'issues': [],
        'expected_behavior': expected_behavior,
        'expected_documents': expected_documents,
    }
    
    if result.error:
        evaluation['status'] = 'ERROR'
        evaluation['issues'].append(f"System error: {result.error}")
        return evaluation
    
    response = result.response
    
    # Check if out-of-scope
    if response.get('out_of_scope'):
        if expected_documents == []:
            evaluation['status'] = 'PASS'
        else:
            evaluation['status'] = 'FAIL'
            evaluation['issues'].append("Query incorrectly classified as non-legal")
        return evaluation
    
    # Check if clarification requested
    if response.get('needs_clarification'):
        if 'clarification' in expected_behavior.lower():
            evaluation['status'] = 'PASS'
        else:
            evaluation['status'] = 'PARTIAL_PASS'
            evaluation['issues'].append("Clarification requested but may not be needed")
        return evaluation
    
    # Check if knowledge gap detected
    if response.get('knowledge_gap_detected'):
        if expected_documents == []:
            evaluation['status'] = 'PASS'
        else:
            evaluation['status'] = 'FAIL'
            evaluation['issues'].append("Knowledge gap detected for answerable question")
        return evaluation
    
    # Check answer quality
    answer = response.get('answer', '')
    
    if not answer or len(answer) < 20:
        evaluation['status'] = 'FAIL'
        evaluation['issues'].append("Answer too short or empty")
        return evaluation
    
    # Check sources
    sources = response.get('sources', [])
    if expected_documents and not sources:
        evaluation['status'] = 'FAIL'
        evaluation['issues'].append("No sources retrieved")
        return evaluation
    
    # Check confidence
    confidence = response.get('confidence_score', 0)
    if confidence < 0.3:
        evaluation['status'] = 'PARTIAL_PASS'
        evaluation['issues'].append(f"Low confidence score: {confidence}")
    
    # If no issues found, mark as pass
    if evaluation['status'] == 'UNKNOWN':
        evaluation['status'] = 'PASS'
    
    return evaluation


def run_critical_tests():
    """Run critical tests first."""
    print("=" * 80)
    print("CRITICAL TESTS")
    print("=" * 80)
    
    results = []
    
    for test_name, test_data in CRITICAL_TESTS.items():
        print(f"\n{test_name}: {test_data['id']}")
        print(f"Question: {test_data['question']}")
        print(f"Expected: {test_data['expected_behavior']}")
        
        result = run_test(test_data['question'], test_data['id'], 'CRITICAL')
        evaluation = evaluate_result(
            result, 
            test_data['expected_behavior'], 
            test_data.get('expected_documents', [])
        )
        result.evaluation = evaluation
        
        print(f"Status: {evaluation['status']}")
        print(f"Response time: {result.response_time_ms:.0f}ms")
        
        if evaluation['issues']:
            print(f"Issues: {evaluation['issues']}")
        
        results.append(result)
    
    return results


def run_category_tests():
    """Run all category tests."""
    print("\n" + "=" * 80)
    print("CATEGORY TESTS")
    print("=" * 80)
    
    results = []
    
    for category_name, tests in TEST_SUITE.items():
        print(f"\n{category_name}")
        print("-" * 80)
        
        for test in tests:
            print(f"\nTest {test['id']}: {test['question'][:60]}...")
            
            result = run_test(
                test['question'], 
                test['id'], 
                category_name
            )
            evaluation = evaluate_result(
                result,
                test.get('expected_behavior', ''),
                test.get('expected_documents', [])
            )
            result.evaluation = evaluation
            
            print(f"Status: {evaluation['status']}")
            print(f"Time: {result.response_time_ms:.0f}ms" if result.response_time_ms else "Time: ERROR")
            
            results.append(result)
    
    return results


def generate_report(results):
    """Generate final test report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(results),
        'passed': 0,
        'partial_pass': 0,
        'failed': 0,
        'error': 0,
        'results': [r.to_dict() for r in results],
    }
    
    for result in results:
        if result.error:
            report['error'] += 1
        elif result.evaluation:
            status = result.evaluation['status']
            if status == 'PASS':
                report['passed'] += 1
            elif status == 'PARTIAL_PASS':
                report['partial_pass'] += 1
            else:
                report['failed'] += 1
    
    return report


def save_report(report):
    """Save report to file."""
    filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {filename}")


def print_summary(report):
    """Print test summary."""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Partial pass: {report['partial_pass']}")
    print(f"Failed: {report['failed']}")
    print(f"Error: {report['error']}")
    
    if report['total_tests'] > 0:
        pass_rate = (report['passed'] / report['total_tests']) * 100
        print(f"Pass rate: {pass_rate:.1f}%")
    
    # Calculate average response time
    times = [r['response_time_ms'] for r in report['results'] if r['response_time_ms']]
    if times:
        avg_time = sum(times) / len(times)
        print(f"Average response time: {avg_time:.0f}ms")


def main():
    """Main test runner."""
    print("Legal QA Test Runner")
    print("=" * 80)
    
    # Check if LLM is available
    print("\nChecking LLM availability...")
    try:
        from legal_information_assistance_system.legal_ai.services.llm import LegalLLM
        llm = LegalLLM()
        print("LLM initialized successfully")
    except Exception as e:
        print(f"LLM initialization failed: {e}")
        print("Please ensure Ollama or OpenAI is configured and running")
        print("Tests cannot proceed without LLM")
        return
    
    # Run critical tests
    critical_results = run_critical_tests()
    
    # Run category tests
    category_results = run_category_tests()
    
    # Generate report
    all_results = critical_results + category_results
    report = generate_report(all_results)
    
    # Save and print report
    save_report(report)
    print_summary(report)


if __name__ == '__main__':
    main()
