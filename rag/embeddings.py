from sentence_transformers import SentenceTransformer
from models import Document

class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate(self, document : Document) -> Document:
        if not document.chunks:
            return document

        document.chunk_embeddings = self.model.encode(
            document.chunks,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).tolist()

        return document