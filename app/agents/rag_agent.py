from app.vectorstore.chroma_store import chroma_store
from app.services.gemini_service import gemini_service

class RagAgent:
    def answer_query(self, query: str) -> str:
        context_docs = chroma_store.search(query, n_results=3)
        context = "\n".join(context_docs) if context_docs else "No se encontró información específica en la base de conocimiento."

        prompt = f"""
        Responde la consulta del usuario usando SOLO el contexto proporcionado.

        Contexto:
        {context}

        Consulta del usuario:
        "{query}"
        """

        response = gemini_service.generate_response(prompt)

        if response is None or "Error processing" in str(response) or "Error calling Gemini" in str(response):
            return f"Según la base de conocimiento: {context}"

        return response