import os
import re
from typing import Dict, List, Any
import pymupdf

class DocumentParser:
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif ext in [".txt", ".md", ".markdown"]:
            return DocumentParser._parse_text_or_markdown(file_path)
        elif ext in [".html", ".htm"]:
            return DocumentParser._parse_html(file_path)
        else:
            return DocumentParser._parse_text_or_markdown(file_path)

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        doc = pymupdf.open(file_path)
        full_text_pages = []
        metadata = {
            "title": doc.metadata.get("title", os.path.basename(file_path)),
            "author": doc.metadata.get("author", "Unknown"),
            "total_pages": len(doc),
            "format": "PDF"
        }
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                full_text_pages.append({
                    "page_number": page_num + 1,
                    "text": text
                })
        doc.close()
        combined_text = "\n\n".join([p["text"] for p in full_text_pages])
        return {
            "file_name": os.path.basename(file_path),
            "metadata": metadata,
            "pages": full_text_pages,
            "full_text": combined_text
        }

    @staticmethod
    def _parse_text_or_markdown(file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        meta = {"title": os.path.basename(file_path), "format": "Text/Markdown"}
        for line in content.splitlines()[:10]:
            if ":" in line:
                key, val = line.split(":", 1)
                clean_key = key.strip().lower().replace(" ", "_")
                if clean_key in ["title", "jurisdiction", "document_type", "citation", "date", "court"]:
                    meta[clean_key] = val.strip()

        return {
            "file_name": os.path.basename(file_path),
            "metadata": meta,
            "pages": [{"page_number": 1, "text": content}],
            "full_text": content
        }

    @staticmethod
    def _parse_html(file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        cleaned = re.sub(r'<[^>]+>', ' ', raw)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return {
            "file_name": os.path.basename(file_path),
            "metadata": {"title": os.path.basename(file_path), "format": "HTML"},
            "pages": [{"page_number": 1, "text": cleaned}],
            "full_text": cleaned
        }