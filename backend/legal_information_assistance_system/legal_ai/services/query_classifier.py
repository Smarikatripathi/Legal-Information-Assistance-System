"""
Query Classifier Service
Classifies user queries as LEGAL, NON_LEGAL, or UNCLEAR
Uses a hybrid approach: keyword rules + LLM fallback
"""

import re
from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from legal_information_assistance_system.legal_ai.services.language import language_service
from legal_information_assistance_system.legal_ai.services.llm import llm
from legal_information_assistance_system.legal_ai.services.prompts import QUERY_CLASSIFIER_PROMPT


@dataclass
class ClassificationResult:
    """Result of query classification."""
    label: str  # "LEGAL", "NON_LEGAL", "UNCLEAR"
    confidence: float
    reason: str
    language: str


class QueryClassifier:
    """Classifies user queries into LEGAL, NON_LEGAL, or UNCLEAR."""
    
    # Legal keywords that indicate a legal query
    LEGAL_KEYWORDS = [
        r"\blaw|legal|right|rights|court|judge|act|code|section|article|constitution|case|judgment|verdict|lawyer|attorney|theft|stolen|crime|criminal|punishment|penalty|offense|police|complaint|report|arrest|warrant|detention|citizenship|property|marriage|divorce|contract|employment|labor|tax|taxation|government|administration|regulation|rule|ordinance|justice|jurisdiction|litigation|sue|lawsuit|evidence|witness|bail|prison|jail|fine|imprisonment|death penalty|capital punishment|fundamental rights|human rights|civil rights|criminal law|civil law|commercial law|family law|corporate law|international law|customs|immigration|visa|passport|permit|license|registration|notary|affidavit|deed|title|lease|rent|tenant|landlord|inheritance|will|trust|probate|bankruptcy|insolvency|debt|credit|loan|mortgage|insurance|intellectual property|copyright|trademark|patent|trade secret|defamation|libel|slander|privacy|data protection|cyber law|environmental law|health law|education law|labor union|strike|lockout|collective bargaining|minimum wage|overtime|workplace safety|discrimination|harassment|sexual harassment|equal opportunity|affirmative action|whistleblower|corruption|bribery|fraud|embezzlement|money laundering|counterfeiting|forgery|perjury|contempt of court|appeal|appellate|supreme court|high court|district court|trial|hearing|plea|guilty|not guilty|acquittal|conviction|sentence|parole|probation|rehabilitation|juvenile|minor|adult|age of consent|statute of limitations|tort|negligence|liability|damages|compensation|restitution|injunction|restraining order|protective order|restraining order|subpoena|discovery|deposition|interrogatory|mediation|arbitration|conciliation|settlement|negotiation|contract breach|breach of contract|void|voidable|unenforceable|consideration|offer|acceptance|capacity|legality|mutual assent|statute|ordinance|regulation|bylaw|charter|constitution|amendment|ratification|referendum|initiative|recall|impeachment|censure|ethics|conflict of interest|recusal|disqualification|bar admission|disbarment|professional conduct|malpractice|negligence|standard of care|duty of care|breach of duty|causation|foreseeability|proximate cause|actual cause|contributory negligence|comparative negligence|strict liability|product liability|premises liability|attractive nuisance|nuisance|trespass|conversion|eminent domain|condemnation|zoning|land use|environmental impact|permit|license|certificate|registration|filing|recording|notarization|authentication|apostille|legalization|attestation|certification|verification|validation|enforcement|compliance|violation|penalty|fine|sanction|remedy|relief|damages|injunction|specific performance|rescission|reformation|restitution|unjust enrichment|quantum meruit|quantum valebant|constructive trust|resulting trust|express trust|implied trust|fiduciary duty|agency|principal|agent|power of attorney|durable power of attorney|springing power of attorney|healthcare proxy|living will|advance directive|guardian|conservator|ward|incapacity|competence|capacity|minority|emancipation|adoption|custody|visitation|support|alimony|spousal support|child support|paternity|maternity|surrogacy|artificial insemination|in vitro fertilization|prenuptial agreement|postnuptial agreement|separation|annulment|divorce|dissolution|domestic partnership|civil union|same-sex marriage|common law marriage|bigamy|polygamy|adultery|infidelity|domestic violence|restraining order|protective order|order of protection",
        r"(कानुन|कानून|अधिकार|अदालत|न्यायाधीश|ऐन|संहिता|धारा|अनुच्छेद|संविधान|मुद्दा|निर्णय|वकील|चोरी|चोर|अपराध|फौजदारी|दण्ड|सजाय|प्रहरी|गुनासो|पक्राउ|वारेन्ट|नागरिकता|सम्पत्ति|विवाह|सम्झौता|रोजगारी|कर|सरकार|प्रशासन|नियम|नियमावली|न्याय|क्षेत्राधिकार|मुद्दा|मुद्दा दायर|साक्षी|जमानत|कारागार|जेल|जरिवाना|कैद|मृत्युदण्ड|मौलिक अधिकार|मानव अधिकार|फौजदारी कानुन|नागरिक कानुन|व्यापारिक कानुन|परिवारिक कानुन|कम्पनी कानुन|अन्तर्राष्ट्रिय कानुन|भन्सार|आप्रवास|भिसा|राहदानी|अनुमति पत्र|लाइसेन्स|दर्ता|नोटरी|शपथ पत्र|सम्झौता|शीर्षक|भाडा|भाडेदार|मालिक|सम्पत्ति|इच्छा पत्र|विश्वास|सम्पत्ति|दिवालिया|ऋण|कर्जा|बन्धक|बीमा|बौद्धिक सम्पत्ति|कपीराइट|ट्रेडमार्क|पेटेन्ट|मानहानि|गोपनीयता|डाटा सुरक्षा|साइबर कानुन|पर्यावरणीय कानुन|स्वास्थ्य कानुन|शिक्षा कानुन|श्रमिक संघ|हडताल|लकआउट|सामूहिक बार्गेनिंग|न्यूनतम तलब|ओभरटाइम|कार्यस्थल सुरक्षा|भेदभाव|उत्पीडन|यौन उत्पीडन|समान अवसर|सकारात्मक कार्य|व्हिसलब्लोअर|भ्रष्टाचार|घुस|धोखादेही|अनैतिक सम्पत्ति|मुद्रा शोधन|नकली|जालसाजी|झूठो गवाही|अदालतको अवमानना|अपील|अपीलीय|सर्वोच्च अदालत|उच्च अदालत|जिल्ला अदालत|मुद्दा|सुनुवाई|गुनाह स्वीकार|दोषी|निर्दोषी|रिहाई|दोषसिद्ध|सजाय|प्यारोल|माफ|पुनर्वास|किशोर|नाबालिग|वयस्क|सहमति उमेर|सीमा|संशोधन|पुष्टिकरण|जनमत|पहल|स्मरण|महाभियोग|निन्दा|नैतिकता|हितको द्वन्द्व|बाहेक|अयोग्यता|बार दर्ता|वकील पदबाट हटाउने|व्यावसायिक आचरण|लापरवाही|मानक|कर्तव्य|कर्तव्य भंग|कारण|पूर्वानुमान|निकट कारण|वास्तविक कारण|योगदानकारी लापरवाही|तुलनात्मक लापरवाही|कडा दायित्व|उत्पाद दायित्व|परिसर दायित्व|आकर्षक खतरा|उपद्रव|अनधिकृत प्रवेश|रूपान्तरण|सार्वजनिक सम्पत्ति|निन्दा|क्षेत्र उपयोग|पर्यावरणीय प्रभाव|अनुमति|लाइसेन्स|प्रमाणपत्र|दर्ता|दाखिला|रेकर्डिंग|नोटरीकरण|प्रमाणीकरण|अपोस्टिल|वैधीकरण|प्रमाण|प्रमाणीकरण|प्रमाणीकरण|प्रमाणीकरण|कार्यान्वयन|अनुपालन|उल्लंघन|दण्ड|जरिवाना|प्रतिबन्ध|उपचार|राहत|क्षतिपूर्ति|निषेधाज्ञा|विशिष्ट प्रदर्शन|रद्द|सुधार|पुनर्स्थापन|अनुचित समृद्धि|क्वान्टम मेरिट|क्वान्टम भेलेबान्ट|निर्माण ट्रस्ट|परिणामी ट्रस्ट|स्पष्ट ट्रस्ट|अप्रत्यक्ष ट्रस्ट|न्यायिक कर्तव्य|एजेन्सी|मुख्य|प्रतिनिधि|वकीलको अधिकार|टिकाउ पावर अफ अटर्नी|स्प्रिङिंग पावर अफ अटर्नी|स्वास्थ्य सेवा प्रोक्सी|जीवित इच्छा|अग्रिम निर्देशन|अभिभावक|संरक्षक|वार्ड|अक्षमता|दक्षता|क्षमता|कम उमेर|मुक्ति|दत्तक ग्रहण|हिरासत|भ्रमण|समर्थन|गुनासो|स्पाउसल सपोर्ट|बाल समर्थन|पितृत्व|मातृत्व|सरोगेसी|कृत्रिम निषेचन|इन भिट्रो फर्टिलाइजेसन|प्री-नप्चुअल सम्झौता|पोस्ट-नप्चुअल सम्झौता|पृथक्करण|रद्द|विवाह विच्छेद|विघटन|घरेलु साझेदारी|नागरिक संघ|समलिंगी विवाह|कमन ल म्यारेज|बहुविवाह|बहुपत्नी प्रथा|व्यभिचार|अविश्वास|घरेलु हिंसा|निषेधाज्ञा|सुरक्षा आदेक्ष|सुरक्षा आदेश)",
    ]
    
    # Non-legal patterns
    NON_LEGAL_PATTERNS = [
        r"\b(joke|jokes|funny|laugh|meme)\b",
        r"\b(weather|temperature|forecast|rain|snow|wind)\b",
        r"\b(movie|movies|film|music|song|actor|actress|celebrity)\b",
        r"\b(recipe|cook|cooking|food|restaurant|pizza|burger|dinner)\b",
        r"\b(cricket|football|basketball|sport|match|score|game|team)\b",
        r"\b(hello|hi|hey|good morning|good evening|how are you|thanks|thank you)\b",
        r"\b(capital|capital city)\s+(of|in|for)\s+(?!nepal|काठमाडौं|kathmandu)",
        r"\b(cristiano ronaldo|messi|lionel messi|neymar|mbappe|virat kohli|sachin tendulkar|roger federer|nadal|djokovic|lebron james|kobe bryant|michael jordan)\b",
        r"(जोक|हासो)",
        r"(खाना|रेसिपी|पकाउने)",
        r"(मौसम|तापक्रम)",
        r"(चलचित्र|फिल्म|गीत|संगीत)",
        r"(क्रिकेट|फुटबल|खेल)",
        r"^[\d\s\+\-\*\/\=\(\)\.]+$",
        r"\b\d+\s*[\+\-\*\/]\s*\d+\s*[=]?\s*\d+",
    ]
    
    # Vague/unclear patterns
    UNCLEAR_PATTERNS = [
        r"^(can i|may i|should i|could i|would i|is it|is this|is that|are you|are we|are they|do i|does it)\s*\??\s*$",
        r"^(yes|no|maybe|ok|okay|sure|alright|fine|good|bad|better|worse)$",
        r"^(के|किन|कसरी|कहाँ|कुन|को|कहिले|कति)\s*\??\s*$",
        r"^(हो|होइन|होला|हुन्छ|हुनेछ|हुनुहुन्छ|हुनुपर्छ)\s*\??\s*$",
        r"^(छ|छैन|छन्|छु|छौ|छौं)\s*\??\s*$",
        r"^(ठीक|ठीक छ|ठीक छैन|ठीक छन्|ठीक छु|ठीक छौ|ठीक छौं)\s*\??\s*$",
        r"^(राम्रो|राम्रो छ|राम्रो छैन|राम्रो छन्|राम्रो छु|राम्रो छौ|राम्रो छौं)\s*\??\s*$",
        r"^(खराब|खराब छ|खराब छैन|खराब छन्|खराब छु|खराब छौ|खराब छौं)\s*\??\s*$",
    ]
    
    def __init__(self):
        self.use_llm_classifier = getattr(settings, "RAG_USE_LLM_CLASSIFIER", False)
    
    def classify(self, query: str) -> ClassificationResult:
        """
        Classify query as LEGAL, NON_LEGAL, or UNCLEAR.
        Uses keyword-based classification first, falls back to LLM if enabled.
        """
        if not query or not query.strip():
            return ClassificationResult(
                label="UNCLEAR",
                confidence=0.0,
                reason="empty_query",
                language="en"
            )
        
        language = language_service.detect_language(query)
        normalized = query.lower().strip()
        
        # Step 1: Check for non-legal patterns
        for pattern in self.NON_LEGAL_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return ClassificationResult(
                    label="NON_LEGAL",
                    confidence=0.95,
                    reason="non_legal_pattern",
                    language=language
                )
        
        # Step 2: Check for vague/unclear patterns
        for pattern in self.UNCLEAR_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return ClassificationResult(
                    label="UNCLEAR",
                    confidence=0.90,
                    reason="vague_query",
                    language=language
                )
        
        # Step 3: Check for legal keywords
        for pattern in self.LEGAL_KEYWORDS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return ClassificationResult(
                    label="LEGAL",
                    confidence=0.85,
                    reason="legal_keyword",
                    language=language
                )
        
        # Step 4: If no clear match, use LLM classifier if enabled
        if self.use_llm_classifier:
            return self._classify_with_llm(query, language)
        
        # Step 5: Default to LEGAL (allow retriever to decide)
        return ClassificationResult(
            label="LEGAL",
            confidence=0.60,
            reason="default_legal",
            language=language
        )
    
    def _classify_with_llm(self, query: str, language: str) -> ClassificationResult:
        """
        Use LLM to classify query when keyword-based classification is inconclusive.
        """
        classification_prompt = QUERY_CLASSIFIER_PROMPT.format(query=query)
        
        try:
            response = llm.generate(
                prompt=classification_prompt,
                system_prompt="You are a legal query classifier. Return ONLY one label: LEGAL, NON_LEGAL, or UNCLEAR.",
                temperature=0.1,
                max_tokens=10
            )
            
            label = response.strip().upper()
            if label not in ["LEGAL", "NON_LEGAL", "UNCLEAR"]:
                # Fallback to LEGAL if LLM returns unexpected output
                label = "LEGAL"
            
            return ClassificationResult(
                label=label,
                confidence=0.75,
                reason="llm_classification",
                language=language
            )
        except Exception as e:
            # Fallback to LEGAL if LLM fails
            return ClassificationResult(
                label="LEGAL",
                confidence=0.50,
                reason="llm_fallback",
                language=language
            )


query_classifier = QueryClassifier()
