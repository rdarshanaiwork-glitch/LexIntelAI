import os
import pytest
from app.rag.parser import DocumentParser
from app.rag.chunker import LegalChunker
from app.rag.vector_store import LegalHybridVectorStore
from app.core.config import settings

def test_document_parser_and_chunker():
    sample_file = os.path.join(settings.SAMPLE_DIR, "statute_contract_law.txt")
    assert os.path.exists(sample_file), "Sample statute file must exist"

    parsed = DocumentParser.parse_file(sample_file)
    assert parsed["file_name"] == "statute_contract_law.txt"
    assert "full_text" in parsed
    assert len(parsed["full_text"]) > 100

    chunker = LegalChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_document(parsed)
    assert len(chunks) >= 1
    assert "text" in chunks[0]
    assert "metadata" in chunks[0]

def test_vector_store_retrieval():
    vs = LegalHybridVectorStore()
    sample_file = os.path.join(settings.SAMPLE_DIR, "precedent_hadley_v_baxendale.md")
    parsed = DocumentParser.parse_file(sample_file)
    chunker = LegalChunker(chunk_size=600, chunk_overlap=100)
    chunks = chunker.chunk_document(parsed)
    vs.add_chunks(chunks)

    results = vs.search("consequential lost profits mill delivery delay", top_k=2)
    assert len(results) > 0
    assert results[0]["is_verified_evidence"] is True
    # The retrieved chunk is the facts of Hadley v Baxendale
    assert "baxendale" in results[0]["source_file"].lower() or "mill" in results[0]["text"].lower()