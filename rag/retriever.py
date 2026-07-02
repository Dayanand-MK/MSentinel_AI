import chromadb
from sentence_transformers import SentenceTransformer
from config.settings import CHROMA_DB_PATH

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH
        )
        self.collection = self.client.get_collection(
            "msentinel_documents"
        )

    def search(self, query: str, top_k: int = 5, where: dict = None):
        embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where,
        )
        return results