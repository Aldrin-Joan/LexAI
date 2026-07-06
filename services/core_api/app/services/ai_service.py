import asyncio
from app.services.rag.rag_service import RAGService
from app.services.translation_service import TranslationService
from app.services.kg.kg_query import KnowledgeGraphQuery


rag_service = RAGService()
translator = TranslationService()
kg_query = KnowledgeGraphQuery()


class AIService:

    @staticmethod
    async def get_legal_advice(query: str) -> tuple[str, str]:
        # Step 1: Detect language
        source_lang = translator.detect_language(query)

        # Step 2: Translate to English if needed
        if source_lang != "en":
            query_en = translator.translate(query, source_lang, "en")
        else:
            query_en = query

        # Step 3: Expand query using Knowledge Graph
        expanded_query_en, sources_list = kg_query.expand_query(query_en)

        # Step 4: Run RAG in background thread (blocking call)
        answer_en = await asyncio.to_thread(rag_service.query, expanded_query_en)

        # Step 4: Translate answer back to original language
        if source_lang != "en":
            final_answer = translator.translate(answer_en, "en", source_lang)
        else:
            final_answer = answer_en

        print("Original Query:", query)
        print("Translated Query:", query_en)
        print("Expanded Query:", expanded_query_en)
        print("Knowledge Graph Sources:", sources_list)
        print("Final Answer:", final_answer)

        return final_answer, sources_list

    @staticmethod
    async def text_to_speech_placeholder(text: str) -> str:
        return "TTS not implemented yet"

    @staticmethod
    async def speech_to_text_placeholder(audio_data: bytes) -> str:
        return "STT not implemented yet"
