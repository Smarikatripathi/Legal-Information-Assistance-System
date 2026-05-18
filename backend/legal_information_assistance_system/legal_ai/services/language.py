from langdetect import detect

class LanguageService:

    def detect_language(self, text: str) -> str:
        """
        Detect language of user query
        """
        try:
            return detect(text)
        except:
            return "en"


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