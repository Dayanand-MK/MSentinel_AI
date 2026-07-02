from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import Document

class Chunker:
    def __init__(self, chunk_size : int = 800, chunk_overlap : int = 150,):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap,)

    def chunk(self, document : Document) -> Document:
        chunks = self.splitter.split_text(document.cleaned_text)

        document.chunks = chunks

        return document