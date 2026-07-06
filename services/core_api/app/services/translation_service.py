from langdetect import detect
from deep_translator import GoogleTranslator


class TranslationService:
    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except:
            return "en"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang:
            return text

        try:
            translated = GoogleTranslator(
                source=source_lang,
                target=target_lang
            ).translate(text)
            return translated
        except:
            return text
