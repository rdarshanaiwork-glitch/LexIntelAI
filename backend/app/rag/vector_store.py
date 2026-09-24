import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings

logger = logging.getLogger('lexintel.vector_store')

class LegalHybridVectorStore:
    def __init__(self, index_dir: str = settings.VECTOR_INDEX_DIR):
        self.index_dir = index_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix = None
        self.index_file = os.path.join(self.index_dir, "legal_index.json")
        os.makedirs(self.index_dir, exist_ok=True)
        self.load()

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        existing_ids = {c["chunk_id"] for c in self.chunks}
        added = 0
        for chunk in new_chunks:
            if chunk["chunk_id"] not in existing_ids:
                self.chunks.append(chunk)
                existing_ids.add(chunk["chunk_id"])
                added += 1
        if added > 0:
            self._rebuild_index()
            self.save()
            logger.info(f"Added {added} chunks to vector store. Total: {len(self.chunks)}")

    def _rebuild_index(self):
        if not self.chunks:
            self.vectorizer = None
            self.matrix = None
            return

        corpus = [c["text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            max_features=15000,
            sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
        source_type: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.chunks or self.vectorizer is None or self.matrix is None:
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.matrix).flatten()

            # Rank items by score
            top_indices = np.argsort(scores)[::-1]

            results = []
            for idx in top_indices:
                score = float(scores[idx])
                if score < 0.05 and len(results) >= 2:
                    continue  # Cut off irrelevant noise if we have at least 2 matches

                chunk = self.chunks[idx]
                meta = chunk.get("metadata", {})

                # Filter by source_type if specified
                if source_type:
                    src_file = chunk.get("source_file", "").lower()
                    chunk_type = meta.get("document_type", "").lower()
                    if not chunk_type:
                        if "precedent" in src_file or meta.get("court"):
                            chunk_type = "precedent"
                        elif "statute" in src_file or "restatement" in src_file or "ucc" in src_file:
                            chunk_type = "statute"
                    if chunk_type and source_type.lower() not in chunk_type:
                        continue

                # Filter by jurisdiction if specified
                if jurisdiction:
                    chunk_jur = meta.get("jurisdiction", "").lower()
                    j_req = jurisdiction.lower()
                    match = (
                        not chunk_jur
                        or chunk_jur in j_req
                        or j_req in chunk_jur
                        or any(w in j_req for w in chunk_jur.split() if len(w) > 3)
                    )
                    if not match:
                        continue

                results.append({
                    "chunk_id": chunk["chunk_id"],
                    "source_file": chunk["source_file"],
                    "page_number": chunk.get("page_number", 1),
                    "section": chunk.get("section", "General"),
                    "text": chunk["text"],
                    "relevance_score": round(score, 4),
                    "metadata": meta,
                    "is_verified_evidence": True  # Explicitly distinguish retrieved ground truth
                })

                if len(results) >= top_k:
                    break

            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def save(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def load(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self._rebuild_index()
                logger.info(f"Loaded {len(self.chunks)} chunks from {self.index_file}")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                self.chunks = []