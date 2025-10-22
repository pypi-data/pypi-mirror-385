"""Document preprocessor for LaTeX RAG system.

This module handles the preprocessing pipeline for different formats of document, including
LaTeX documents before they are used before they are used in the RAG (Retrieval-Augmented Generation) system.
It orchestrates the parsing of documents using utility modules such the LatexParser and converts the structured content into
chunked text segments suitable for embedding and vector storage.

Key responsibilities:
- Provide a unified interface for parsing different formats of documents
- Parse documents into structured data (chapters, sections, paragraphs, citations)
- Chunk documents into fixed-size segments (768 tokens) with overlap (100-150 tokens)
- Prepare clean text content for the embedding engine
- Maintain document structure and citation relationships

The preprocessor returns structured chunks with metadata that can be directly fed to
the embedding engine for vector database storage.
"""

import os

from ..utils.latex_parser import LatexDocument, LatexParser
from .data_chunker import DataChunk, DataChunker


class DocumentPreprocessor:
    """Document preprocessor for different formats of documents in RAG system.

    This class orchestrates the complete preprocessing pipeline for different formats of documents,
    from parsing to chunking, preparing them for embedding and vector storage.

    Attributes:
        chunker: DataChunker instance for chunking documents
        chunk_size: Size of text chunks in tokens (default: 768)
        overlap_size: Overlap between chunks in tokens (default: 100-150)
    """

    def __init__(
        self,
        chunker: DataChunker = None,
        chunk_size: int = 768,
        overlap_size: int = 100,
    ):
        """Initialize the DocumentPreprocessor.

        Args:
            chunk_size: Size of text chunks in tokens (default: 768)
            overlap_size: Overlap between chunks in tokens (default: 100-150)
        """
        self.chunker = (
            chunker if chunker is not None else DataChunker(chunk_size, overlap_size)
        )
        self.file_extension_map = {
            "latex": [".tex", ".latex", ".bib"],
            "pdf": [".pdf"],
            "docx": [".docx"],
            "doc": [".doc"],
            "txt": [".txt"],
        }

        self.latex_parser = LatexParser()

    def preprocess_document(
        self, file_path: str, format: str = "latex"
    ) -> list[DataChunk]:
        """Preprocess the document and return a list of DataChunks.

        Args:
            file_path: Path to the document file
            format: Format of the document (default: "latex")

        Returns:
            list[DataChunk]: List of DataChunks with metadata
        """
        if format == "latex":
            if file_path.endswith(".bib"):
                self.latex_parser.parse_bibliography(file_path)
            else:
                document = self.latex_parser.parse_document(file_path)
        else:
            raise ValueError(f"Unsupported document format: {format}")

        return self._chunk_documents([document])

    def preprocess_documents(
        self, file_paths: list[str], format: str = "latex"
    ) -> list[DataChunk]:
        """Preprocess the documents and return a list of DataChunks."""
        if format == "latex":
            # Find the bibliography file
            bibliography_path = None
            for file_path in file_paths:
                if file_path.endswith(".bib"):
                    bibliography_path = file_path
                    break
            if bibliography_path:
                self.latex_parser.parse_bibliography(bibliography_path)
            documents = [
                self.latex_parser.parse_document(file_path)
                for file_path in file_paths
                if file_path != bibliography_path
            ]
            return self._chunk_documents(documents)
        else:
            raise ValueError(f"Unsupported document format: {format}")

    def preprocess_document_folder(
        self, folder_path: str, format: str = "latex"
    ) -> list[DataChunk]:
        """Preprocess the documents in the folder and return a list of DataChunks."""
        file_paths = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if any(file.endswith(ext) for ext in self.file_extension_map[format])
        ]
        return self.preprocess_documents(file_paths, format)

    def _extract_document_text(self, documentList: list[LatexDocument]) -> str:
        """Extract the text from the document.

        Args:
            documentList: list[LatexDocument]
            Each document in the list is a separate document.

        Returns:
            str: The text from the documents
        """
        content_parts = []

        for document in documentList:
            # Extract from chapters
            if document.chapters:
                for chapter in document.chapters:
                    content_parts.append(f"# {chapter.title}")
                    if chapter.paragraphs:
                        for para in chapter.paragraphs:
                            content_parts.append(para.content)
                    if chapter.sections:
                        for section in chapter.sections:
                            content_parts.append(f"## {section.title}")
                            if section.paragraphs:
                                for para in section.paragraphs:
                                    content_parts.append(para.content)

            # Extract from standalone sections
            if document.sections:
                for section in document.sections:
                    content_parts.append(f"## {section.title}")
                    if section.paragraphs:
                        for para in section.paragraphs:
                            content_parts.append(para.content)

            # Extract from standalone paragraphs
            if document.paragraphs:
                for para in document.paragraphs:
                    content_parts.append(para.content)

            # Extract from tables
            if document.tables:
                for table in document.tables:
                    content_parts.append(table.to_plain_text())

        return "\n\n".join(content_parts)

    def _chunk_documents(self, documentList: list[LatexDocument]) -> list[DataChunk]:
        """Chunk the documents into a list of DataChunks."""
        chunks = []
        if not documentList:
            return chunks
        for document in documentList:
            chunks.extend(self._chunk_document(document))
        return chunks

    def _chunk_document(self, document: LatexDocument) -> list[DataChunk]:
        """Chunk the document into a list of DataChunks."""
        if document is None:
            raise ValueError("Document cannot be None")
        chunks = []
        if document.paragraphs:
            paragraph_content = ""
            for paragraph in document.paragraphs:
                paragraph_content += paragraph.content
            chunks.extend(
                self.chunker.chunk(
                    paragraph_content,
                    chunk_type="text",
                    source_document=document.source_document,
                    page_number=None,
                    section_title=document.title,
                    created_at=None,
                )
            )
        if document.chapters:
            for chapter in document.chapters:
                chapter_content = f"# {chapter.title}"
                if chapter.paragraphs:
                    for paragraph in chapter.paragraphs:
                        chapter_content += paragraph.content
                    chunks.extend(
                        self.chunker.chunk(
                            chapter_content,
                            chunk_type="text",
                            source_document=document.source_document,
                            page_number=None,
                            section_title=chapter.title,
                            created_at=None,
                        )
                    )
                if chapter.sections:
                    for section in chapter.sections:
                        section_content = f"## {section.title}"
                        if section.paragraphs:
                            for paragraph in section.paragraphs:
                                section_content += paragraph.content
                            chunks.extend(
                                self.chunker.chunk(
                                    section_content,
                                    chunk_type="text",
                                    source_document=document.source_document,
                                    page_number=None,
                                    section_title=section.title,
                                    created_at=None,
                                )
                            )
        if document.sections:
            for section in document.sections:
                section_content = f"## {section.title}"
                if section.paragraphs:
                    for paragraph in section.paragraphs:
                        section_content += paragraph.content
                    chunks.extend(
                        self.chunker.chunk(
                            section_content,
                            chunk_type="text",
                            source_document=document.source_document,
                            page_number=None,
                            section_title=section.title,
                            created_at=None,
                        )
                    )
        if document.tables:
            for table in document.tables:
                table_content = table.to_plain_text()
                chunks.extend(
                    self.chunker.chunk(
                        table_content,
                        chunk_type="text",
                        source_document=document.source_document,
                        page_number=None,
                        section_title=document.title,
                        created_at=None,
                    )
                )
        return chunks
