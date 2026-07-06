from app.services.rag.rag_service import RAGService

rag = RAGService()

response = rag.query("What is Article 21?")
print(response)
