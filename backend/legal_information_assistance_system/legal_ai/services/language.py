import re
from typing import Pattern

from langdetect import detect


class LanguageService:
    LEGAL_TERM_TRANSLATIONS: list[tuple[Pattern[str], str]] = [
        (re.compile(r"\bcustoms regulation(s)?\b", re.I), "भन्सार नियमावली"),
        (re.compile(r"\bcustoms rule(s)?\b", re.I), "भन्सार नियम"),
        (re.compile(r"\bcustoms\b", re.I), "भन्सार"),
        (re.compile(r"\bregulation(s)?\b", re.I), "नियमावली"),
        (re.compile(r"\brule(s)?\b", re.I), "नियम"),
        (re.compile(r"\bsection(s)?\b", re.I), "धारा"),
        (re.compile(r"\barticle(s)?\b", re.I), "अनुच्छेद"),
        (re.compile(r"\bclause(s)?\b", re.I), "उपधारा"),
        (re.compile(r"\bsubrule(s)?\b", re.I), "उपधारा"),
        (re.compile(r"\bchapter(s)?\b", re.I), "अध्याय"),
        (re.compile(r"\bpart(s)?\b", re.I), "भाग"),
        (re.compile(r"\bact(s)?\b", re.I), "ऐन"),
        (re.compile(r"\blaw(s)?\b", re.I), "कानुन"),
        (re.compile(r"\bcode\b", re.I), "संहिता"),
        (re.compile(r"\bconstitution\b", re.I), "संविधान"),
        (re.compile(r"\bcivil code\b", re.I), "नागरिक संहिता"),
        (re.compile(r"\bcriminal code\b", re.I), "दण्ड संहिता"),
        (re.compile(r"\bjudgment\b", re.I), "निर्णय"),
        (re.compile(r"\bcourt decision\b", re.I), "निर्णय"),
    ]

    DOCUMENT_ALIASES: dict[str, list[str]] = {
        "constitution": ["constitution", "sanvidhan", "संविधान"],
        "civil_code": ["civil code", "nagarik sanhita", "नागरिक संहिता"],
        "criminal_code": ["criminal code", "muluki yin", "दण्ड संहिता"],
        "regulation": ["regulation", "niyamawali", "नियमावली"],
        "act": ["act", "ain", "ऐन"],
        "court_decision": ["court decision", "judgment", "निर्णय"],
    }

    def detect_language(self, text: str) -> str:
        """
        Detect language of user query with improved accuracy for mixed content.
        Returns: 'en' (English), 'ne' (Nepali), or 'ne_roman' (Roman Nepali)
        Prioritizes Nepali when Devanagari characters are present.
        """
        if not text or not text.strip():
            return "en"

        # Check for Devanagari characters first (more reliable than langdetect for Nepali)
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.replace(' ', ''))
        
        # If more than 15% of characters are Devanagari, classify as Nepali
        if total_chars > 0 and devanagari_chars / total_chars > 0.15:
            return "ne"

        # Check for Roman Nepali patterns (Nepali words written in Latin script)
        roman_nepali_indicators = ['ko', 'ka', 'ke', 'ki', 'le', 'la', 'bata', 'dai', 'didi', 'cha', 'cha', 'ho', 'ho', 'ho', 'ho']
        text_lower = text.lower()
        roman_nepali_count = sum(1 for word in roman_nepali_indicators if word in text_lower.split())
        
        # If multiple Roman Nepali indicators found, classify as Roman Nepali
        if roman_nepali_count >= 2:
            return "ne_roman"

        try:
            detected = detect(text)
            # langdetect can be unreliable for short queries, double-check with character analysis
            if detected == "ne":
                return "ne"
            if detected == "en" and devanagari_chars > 0:
                # langdetect said English but we have Devanagari - trust the characters
                return "ne"
            return detected
        except Exception:
            # Fallback to character-based detection
            if devanagari_chars > 0:
                return "ne"
            return "en"

    def translate_legal_query_to_nepali(self, query: str) -> str:
        """
        Normalize English legal queries into Nepali legal terminology.
        """
        if not query or not query.strip():
            return query

        translated = query
        for pattern, replacement in self.LEGAL_TERM_TRANSLATIONS:
            translated = pattern.sub(replacement, translated)
        return translated

    def normalize_query(self, query: str) -> str:
        """
        Normalize whitespace and casing for keyword matching.
        """
        if not query:
            return ""
        return re.sub(r"\s+", " ", query.strip().lower())

    def document_name_matches(self, query: str, document_name: str) -> bool:
        """
        Check whether the query refers to a known document alias.
        """
        if not query or not document_name:
            return False

        normalized_query = self.normalize_query(query)
        normalized_doc = document_name.lower()

        if normalized_doc in normalized_query:
            return True

        for aliases in self.DOCUMENT_ALIASES.values():
            for alias in aliases:
                if alias in normalized_query and alias in normalized_doc:
                    return True
        return False

    def to_english(self, text: str) -> str:
        """
        Convert Nepali → English (optional improvement)
        Replace with Google Translate / deep translator
        """

        # placeholder (replace with real translator)
        return text


    def to_local(self, text: str, lang: str) -> str:
        """
        Convert response back to user language
        """

        return text


language_service = LanguageService()