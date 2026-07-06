import requests


class Generator:
    def __init__(self, model="mistral"):
        self.model = model

    def generate(self, question, context):
        prompt = f"""
You are an Indian legal assistant AI.

Use ONLY the provided legal context to answer the question.

If relevant legal information is found:
- Summarize clearly.
- Mention relevant case names or legal provisions.
- Keep the answer structured and professional.

If information is NOT found in context:
- Clearly state that it is not available in the retrieved documents.
- Do NOT hallucinate.
- Suggest consulting a lawyer if appropriate.

Legal Context:
{context}

Question:
{question}

Answer:
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]
