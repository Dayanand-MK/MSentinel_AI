import chromadb
from config.settings import CHROMA_DB_PATH
from models import Document

class ChromaManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name="msentinel_documents"
        )

    def store(self, document: Document) -> Document:

        ids = []

        for i, chunk in enumerate(document.chunks):

            vector_id = f"{document.original_name}_{i}"

            ids.append(vector_id)

            self.collection.add(
                ids=[vector_id],
                embeddings=[document.chunk_embeddings[i]],
                documents=[chunk],
                metadatas=[{
                    "document": document.original_name,
                    "chunk": i,
                    "risk": document.risk_level,
                }]
            )

        document.vector_ids = ids

        return document