"""
Legal QA Test Suite
Comprehensive test questions for evaluating the Legal Information Assistance System
"""

TEST_SUITE = {
    "CATEGORY_A_SIMPLE_LEGAL": [
        {
            "id": "A1",
            "question": "What should I do if someone steals my property?",
            "expected_behavior": "Retrieve theft provisions from Criminal Code, explain legal steps",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "A2",
            "question": "What are my rights if someone damages my property?",
            "expected_behavior": "Retrieve property damage provisions, explain rights",
            "expected_documents": ["मुलुकी देवानी संहिता ऐन २०७४"],
        },
        {
            "id": "A3",
            "question": "What should I do if I am accused of a crime?",
            "expected_behavior": "Retrieve accused rights provisions, explain legal procedures",
            "expected_documents": ["मुलुकी फौजदारी कार्यविधि संहिता, २०७४(4)"],
        },
    ],
    
    "CATEGORY_B_SCENARIO_BASED": [
        {
            "id": "B1",
            "question": "Someone stole my gold from my bag. What can I do?",
            "expected_behavior": "Retrieve theft provisions, explain reporting and legal action",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "B2",
            "question": "Someone took my phone without my permission. What legal action can I take?",
            "expected_behavior": "Retrieve theft provisions, explain legal options",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "B3",
            "question": "Someone damaged my property intentionally. What can I do?",
            "expected_behavior": "Retrieve property damage provisions",
            "expected_documents": ["मुलुकी देवानी संहिता ऐन २०७४"],
        },
    ],
    
    "CATEGORY_C_NATURAL_LANGUAGE": [
        {
            "id": "C1",
            "question": "Someone took my stuff from my bag. What should I do now?",
            "expected_behavior": "Understand theft intent, retrieve relevant provisions",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "C2",
            "question": "My neighbor broke my fence. What can I do?",
            "expected_behavior": "Retrieve property damage provisions",
            "expected_documents": ["मुलुकी देवानी संहिता ऐन २०७४"],
        },
    ],
    
    "CATEGORY_D_MISSPELLINGS": [
        {
            "id": "D1",
            "question": "Somone stoled my gold. What can I do?",
            "expected_behavior": "Correct or handle typo, retrieve theft provisions",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "D2",
            "question": "Wat are my rights if property is damaged?",
            "expected_behavior": "Handle typo, retrieve property rights",
            "expected_documents": ["मुलुकी देवानी संहिता ऐन २०७४"],
        },
    ],
    
    "CATEGORY_E_SHORT_QUESTIONS": [
        {
            "id": "E1",
            "question": "What is theft?",
            "expected_behavior": "Define theft from Criminal Code",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "E2",
            "question": "Can I report this?",
            "expected_behavior": "Explain reporting procedures",
            "expected_documents": ["मुलुकी फौजदारी कार्यविधि संहिता, २०७४(4)"],
        },
        {
            "id": "E3",
            "question": "What are my rights?",
            "expected_behavior": "Ask clarification or provide general rights",
            "expected_behavior": "Ask clarification (too vague)",
        },
    ],
    
    "CATEGORY_F_LONG_QUESTIONS": [
        {
            "id": "F1",
            "question": "I was walking home from work yesterday evening when someone approached me from behind, grabbed my bag containing my laptop, wallet, and important documents, and ran away. I filed a complaint at the local police station, but they haven't taken any action yet. What legal options do I have to ensure my case is properly investigated and to recover my stolen items?",
            "expected_behavior": "Retrieve theft provisions, police complaint procedures",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४", "मुलुकी फौजदारी कार्यविधि संहिता, २०७४(4)"],
        },
    ],
    
    "CATEGORY_G_SPECIFIC_LEGAL_REFERENCES": [
        {
            "id": "G1",
            "question": "What does Article 2 of the Criminal Code say about theft?",
            "expected_behavior": "Retrieve specific article from Criminal Code",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "G2",
            "question": "What is the punishment for theft under the Criminal Code?",
            "expected_behavior": "Retrieve punishment provisions",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
    ],
    
    "CATEGORY_H_MULTI_TURN": [
        {
            "id": "H1",
            "question": "Someone stole my property.",
            "follow_up": "It was gold jewelry worth 50,000 rupees.",
            "expected_behavior": "Combine context, retrieve theft provisions",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
    ],
    
    "CATEGORY_I_UNKNOWN_TERMS": [
        {
            "id": "I1",
            "question": "Someone stole atqr from my bag. What can I do?",
            "expected_behavior": "Ask clarification about 'atqr' (DO NOT assume ATM)",
            "expected_behavior": "Ask clarification",
        },
        {
            "id": "I2",
            "question": "Someone stole xyz123 from my house. What should I do?",
            "expected_behavior": "Ask clarification about 'xyz123'",
            "expected_behavior": "Ask clarification",
        },
    ],
    
    "CATEGORY_J_NON_LEGAL": [
        {
            "id": "J1",
            "question": "What is the weather today?",
            "expected_behavior": "Return out-of-scope response",
            "expected_documents": [],
        },
        {
            "id": "J2",
            "question": "How do I cook rice?",
            "expected_behavior": "Return out-of-scope response",
            "expected_documents": [],
        },
        {
            "id": "J3",
            "question": "Who won yesterday's football match?",
            "expected_behavior": "Return out-of-scope response",
            "expected_documents": [],
        },
    ],
    
    "CATEGORY_K_OUT_OF_KNOWLEDGE_BASE": [
        {
            "id": "K1",
            "question": "What are the copyright laws for software in Nepal?",
            "expected_behavior": "Detect insufficient evidence, create Knowledge Gap",
            "expected_documents": [],
        },
        {
            "id": "K2",
            "question": "What are the tax implications of cryptocurrency trading in Nepal?",
            "expected_behavior": "Detect insufficient evidence, create Knowledge Gap",
            "expected_documents": [],
        },
    ],
    
    "CATEGORY_L_MULTILINGUAL": [
        {
            "id": "L1",
            "question": "मेरो सामान चोरी भयो। म के गर्नुपर्छ?",
            "expected_behavior": "Retrieve theft provisions, respond in Nepali",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
        {
            "id": "L2",
            "question": "Someone stole my property. म के गर्नुपर्छ?",
            "expected_behavior": "Handle mixed language, retrieve provisions",
            "expected_documents": ["मुलुकी अपराध संहिता २०७४"],
        },
    ],
}

# Critical tests
CRITICAL_TESTS = {
    "HALLUCINATION_TEST": {
        "id": "CRITICAL_1",
        "question": "Someone stole atqr from my bag. What can I do?",
        "expected_behavior": "Ask clarification about 'atqr' (DO NOT assume ATM)",
        "failure_if": "Answers about ATM card without clarification",
    },
    "LEGAL_RETRIEVAL_TEST": {
        "id": "CRITICAL_2",
        "question": "Someone stole my gold from my bag. What can I do?",
        "expected_behavior": "Retrieve theft provisions, NOT unrelated provisions",
        "failure_if": "Retrieves unrelated provisions (e.g., explosives)",
    },
    "KNOWLEDGE_GAP_TEST": {
        "id": "CRITICAL_3",
        "question": "What are the copyright laws for AI-generated content in Nepal?",
        "expected_behavior": "Detect insufficient evidence, create Knowledge Gap",
        "failure_if": "Invents copyright provisions",
    },
}
