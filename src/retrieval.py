from __future__ import annotations

import math
import re
from dataclasses import replace
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models import Document, EvidenceChunk

_WORD_RE = re.compile(r"\w+", flags=re.UNICODE)


def simple_tokens(text: str) -> list[str]:
    return [x.lower() for x in _WORD_RE.findall(text)]


def chunk_documents(docs: list[Document], chunk_words: int = 420, overlap_words: int = 65) -> list[EvidenceChunk]:
    chunks: list[EvidenceChunk] = []
    for doc in docs:
        raw_sections = re.split(r"\n\s*\n|(?=\[Page \d+\])", doc.text)
        section_texts = [s.strip() for s in raw_sections if s.strip()]
        if not section_texts:
            section_texts = [doc.text]
        counter = 0
        for section in section_texts:
            page = None
            page_match = re.search(r"\[Page (\d+)\]", section)
            if page_match:
                page = int(page_match.group(1))
            words = section.split()
            if not words:
                continue
            if len(words) <= chunk_words:
                counter += 1
                chunks.append(EvidenceChunk(f"{doc.doc_id}-c{counter}", doc.doc_id, doc.title, section, page=page, metadata=doc.metadata))
            else:
                step = max(1, chunk_words - overlap_words)
                for start in range(0, len(words), step):
                    window = words[start : start + chunk_words]
                    if not window:
                        break
                    counter += 1
                    chunks.append(EvidenceChunk(f"{doc.doc_id}-c{counter}", doc.doc_id, doc.title, " ".join(window), page=page, metadata=doc.metadata))
                    if start + chunk_words >= len(words):
                        break
    return chunks


class EvidenceRetriever:
    def __init__(self, chunks: list[EvidenceChunk], gemini_client = None):
        self.chunks = chunks
        self.gemini_client = gemini_client
        self.vector_embeddings = None
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None

        if chunks and gemini_client and gemini_client.configured:
            try:
                import numpy as np
                texts = [c.text for c in chunks]
                embeddings = []
                for i in range(0, len(texts), 50):
                    batch = texts[i : i + 50]
                    batch_embs = gemini_client.embed_texts(batch)
                    if batch_embs:
                        embeddings.extend(batch_embs)
                if len(embeddings) == len(chunks):
                    self.vector_embeddings = np.array(embeddings)
            except Exception:
                self.vector_embeddings = None

        if chunks:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
            self.matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def search(self, query: str, top_k: int = 6) -> list[EvidenceChunk]:
        if not self.chunks:
            return []

        # Try Vector Search first
        if self.vector_embeddings is not None and self.gemini_client:
            try:
                import numpy as np
                q_emb = self.gemini_client.embed_text(query)
                if q_emb:
                    q_v = np.array(q_emb).reshape(1, -1)
                    sims = cosine_similarity(q_v, self.vector_embeddings).flatten()
                    order = sims.argsort()[::-1][:top_k]
                    out: list[EvidenceChunk] = []
                    for idx in order:
                        score = float(sims[idx])
                        if score <= 0.05 and len(out) >= 2:
                            continue
                        normalized_score = round(max(0.0, min(1.0, score)), 4)
                        out.append(replace(self.chunks[int(idx)], score=normalized_score))
                    return out
            except Exception:
                pass

        # Fallback to TF-IDF search
        if self.vectorizer is None or self.matrix is None:
            return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix).flatten()
        order = sims.argsort()[::-1][:top_k]
        out: list[EvidenceChunk] = []
        for idx in order:
            score = float(sims[idx])
            if score <= 0 and len(out) >= 2:
                continue
            out.append(replace(self.chunks[int(idx)], score=round(score, 4)))
        return out



def keyword_overlap_score(text: str, keywords: list[str]) -> float:
    lower = text.lower()
    hits = 0
    weighted = 0.0
    for kw in keywords:
        kwl = kw.lower()
        if kwl in lower:
            hits += 1
            weighted += 1.5 if " " in kwl else 1.0
    return weighted / max(1.0, len(keywords))


def best_quote(text: str, keywords: list[str], max_chars: int = 550) -> str:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    scored = []
    for sent in sentences:
        if not sent.strip():
            continue
        score = keyword_overlap_score(sent, keywords)
        scored.append((score, sent.strip()))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        quote = scored[0][1]
    else:
        quote = text.strip()
    if len(quote) > max_chars:
        quote = quote[: max_chars - 3].rstrip() + "..."
    return quote
