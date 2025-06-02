from langchain_community.document_loaders import PyMuPDFLoader
import os
from typing import List
from langchain.schema import Document

def extract_text_from_pdf(pdf_path: str) -> List[Document]:
    """Extracts text from a PDF file using PyMuPDFLoader. """
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    return documents

def save_extracted_text(documents: List[Document], output_path: str):
    """Saves the extracted text to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(doc.page_content)
