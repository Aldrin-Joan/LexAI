from .retriever import Retriever
from .generator import Generator


class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def query(self, user_query):
        # 🔥 Retriever now handles embedding internally
        retrieved_chunks = self.retriever.search(user_query, top_k=8)

        # Extract only text field
        context = "\n\n".join(
            chunk["text"] for chunk in retrieved_chunks
        )

        answer = self.generator.generate(user_query, context)

        return answer
