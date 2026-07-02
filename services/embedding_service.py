from models import Document
from rag import Chunker, EmbeddingGenerator, ChromaManager

class EmbeddingService:
    def __init__(self):
        self.chunker = Chunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = ChromaManager()

    def process_embeddings(self, document: Document) -> Document:
        document = self.chunker.chunk(document)
        document = self.embedding_generator.generate(document)
        document = self.vector_store.store(document)
        return document
