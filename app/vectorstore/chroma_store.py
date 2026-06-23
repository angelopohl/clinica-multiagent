import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

class ChromaStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: list[str], ids: list[str]):
        self.collection.add(documents=documents, ids=ids)

    def search(self, query: str, n_results: int = 2) -> list[str]:
        if self.collection.count() == 0:
            return []
        results = self.collection.query(query_texts=[query], n_results=n_results)
        if results['documents'] and len(results['documents']) > 0:
            return results['documents'][0]
        return []

chroma_store = ChromaStore()
