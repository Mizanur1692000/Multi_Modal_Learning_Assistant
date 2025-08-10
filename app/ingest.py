import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pdfplumber
from typing import List
import uuid

# Define MODEL_NAME here before the class
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class DocumentStore:
    def __init__(self, model_name=MODEL_NAME, dim=384):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dim)
        self.texts = []  # parallel list of text pieces
        self.ids = []

    def ingest_pdf(self, path: str):
        txt = ""
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                txt += "\n" + (p.extract_text() or "")
        self._ingest_text(txt)

    def ingest_txt(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        self._ingest_text(txt)

    def _split_text(self, text: str, chunk_size=400, overlap=50) -> List[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i:i+chunk_size]
            chunks.append(" ".join(chunk))
            i += chunk_size - overlap
        return chunks

    def _ingest_text(self, text: str):
        pieces = self._split_text(text)
        embeddings = self.model.encode(pieces, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)
        for p in pieces:
            self.texts.append(p)
            self.ids.append(str(uuid.uuid4()))

    def retrieve(self, query: str, k: int = 4):
        if len(self.texts) == 0:
            return []
        q_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, k)
        results = []
        for idx in I[0]:
            if idx == -1:  # skip invalid index from faiss
                continue
            if idx < len(self.texts):
                results.append(self.texts[idx])
        return results


# Create a global STORE instance after the class definition
STORE = DocumentStore()