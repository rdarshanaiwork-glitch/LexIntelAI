import re
from typing import List, Dict, Any

class LegalChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = []
        doc_name = parsed_doc.get("file_name", "document")
        doc_meta = parsed_doc.get("metadata", {})
        pages = parsed_doc.get("pages", [])

        chunk_idx = 0
        for page in pages:
            page_num = page.get("page_number", 1)
            page_text = page.get("text", "")
            if not page_text.strip():
                continue

            # Split by major headings or paragraphs
            paragraphs = re.split(r'\n\s*\n', page_text)
            current_chunk = ""
            current_section = "General"

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # Check if paragraph is a section header
                if re.match(r'^(SECTION|ARTICLE|CLAUSE|##|\bCOUNT\b|\bCLAIM\b|\bHOLDING\b)', para, re.IGNORECASE):
                    current_section = para.split("\n")[0][:80]

                if len(current_chunk) + len(para) > self.chunk_size and len(current_chunk) > 200:
                    chunks.append({
                        "chunk_id": f"{doc_name}_p{page_num}_c{chunk_idx}",
                        "source_file": doc_name,
                        "page_number": page_num,
                        "section": current_section,
                        "text": current_chunk.strip(),
                        "metadata": {
                            **doc_meta,
                            "section": current_section,
                            "page_number": page_num
                        }
                    })
                    chunk_idx += 1
                    # Keep overlap from the end of current_chunk
                    overlap_len = min(len(current_chunk), self.chunk_overlap)
                    current_chunk = current_chunk[-overlap_len:] + " " + para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para

            if current_chunk.strip():
                chunks.append({
                    "chunk_id": f"{doc_name}_p{page_num}_c{chunk_idx}",
                    "source_file": doc_name,
                    "page_number": page_num,
                    "section": current_section,
                    "text": current_chunk.strip(),
                    "metadata": {
                        **doc_meta,
                        "section": current_section,
                        "page_number": page_num
                    }
                })
                chunk_idx += 1

        return chunks