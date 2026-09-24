import os
import glob
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.rag.parser import DocumentParser
from app.rag.chunker import LegalChunker
from app.rag.vector_store import LegalHybridVectorStore

logger = logging.getLogger('lexintel.knowledge')

class KnowledgeService:
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = LegalChunker()
        self.vector_store = LegalHybridVectorStore()

    def bootstrap_sample_knowledge(self):
        """Pre-indexes public-domain legal statutes and precedents if vector store is empty."""
        if len(self.vector_store.chunks) > 0:
            logger.info(f"Vector store already contains {len(self.vector_store.chunks)} chunks.")
            return

        logger.info("Bootstrapping sample legal knowledge base from data/sample/...")
        sample_files = glob.glob(os.path.join(settings.SAMPLE_DIR, "*.*"))
        for fpath in sample_files:
            try:
                self.ingest_file(fpath)
            except Exception as e:
                logger.error(f"Failed to ingest sample file {fpath}: {e}")

    def ingest_file(self, file_path: str) -> List[Dict[str, Any]]:
        parsed = self.parser.parse_file(file_path)
        chunks = self.chunker.chunk_document(parsed)
        self.vector_store.add_chunks(chunks)
        logger.info(f"Ingested {file_path}: created {len(chunks)} chunks.")
        return chunks

    def search_all(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vector_store.search(query=query, top_k=top_k)

    def search_statutes(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        return self.vector_store.search(query=query, top_k=top_k, source_type="statute")

    def search_precedents(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        return self.vector_store.search(query=query, top_k=top_k, source_type="precedent")

knowledge_service = KnowledgeService()