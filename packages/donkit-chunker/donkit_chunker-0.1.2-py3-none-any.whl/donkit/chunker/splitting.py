from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from .config import ChunkerConfig, SplitterType


class DonkitChunker:
    def __init__(self, config: ChunkerConfig = ChunkerConfig()):
        self._config = config

    @staticmethod
    def __get_file_content(file_path: str) -> str | dict:
        """
        Retrieve file content from S3.

        Args:
            file_path: Path to the file in S3

        Returns:
            Contents of the file as a string

        Raises:
            ValueError: If the file cannot be found or accessed
            Exception: For other S3 errors
        """
        with open(file_path, encoding="utf-8") as file:
            return file.read()

    def chunk_text(
        self,
        content: str,
        filename: str | None = None,
    ) -> list[Document]:
        if self._config.splitter == "json":
            text = content if isinstance(content, str) else json.dumps(content)
            try:
                json_data = json.loads(text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON content: {e}")
            return self._json_split(
                json_data, self._config.chunk_size, self._config.chunk_overlap, filename
            )

        # Otherwise treat content as text
        text = content if isinstance(content, str) else json.dumps(content)
        match self._config.splitter:
            case SplitterType.CHARACTER:
                return self._character_split(
                    text, self._config.chunk_size, self._config.chunk_overlap, filename
                )
            case SplitterType.SENTENCE:
                return self._sentence_split(
                    text, self._config.chunk_size, self._config.chunk_overlap, filename
                )
            case SplitterType.PARAGRAPH:
                return self._paragraph_split(
                    text, self._config.chunk_size, self._config.chunk_overlap, filename
                )
            case _:
                # Default to semantic splitting
                return self._semantic_split(
                    text, self._config.chunk_size, self._config.chunk_overlap, filename
                )

    def chunk_file(
        self,
        file_path: str,
    ) -> list[Document]:
        """
        Chunk the text from a file according to the specified parameters.

        Args:
            file_path:

        Returns:
            List of text chunks

        Raises:
            ValueError: If file content is empty or exceeds maximum allowed length
        """
        file_content: str | dict = self.__get_file_content(file_path)
        if not file_content:
            raise ValueError("File content is empty")

        # Extract filename from path
        filename = Path(file_path).name
        # Generate document_id for all chunks of this file
        document_id = str(uuid4())

        chunks = self.chunk_text(file_content, filename=filename)
        # Add document_id to all chunks
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
        return chunks

    @staticmethod
    def _json_split(
        json_data: dict, max_chunk_size: int, overlap: int, filename: str | None = None
    ) -> list[Document]:
        """
        Split JSON data into chunks.

        Args:
            json_data: The JSON data to chunk
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of JSON chunks
        """
        content = json_data.get("content", {})
        if not content:
            raise ValueError("JSON data is empty or missing 'content' key")
        documents = []
        for page in content:
            if isinstance(page, str):
                metadata = {"page_number": 0, "type": "text"}
                if filename:
                    metadata["filename"] = filename
                documents.append(
                    Document(
                        page_content=page,
                        metadata=metadata,
                    )
                )
                continue
            # Extract metadata fields
            metadata = {
                "page_number": page.get("page", 0),
                "type": page.get("type", "text"),
            }
            if filename:
                metadata["filename"] = filename
            page_content = page.get("content", {})
            page_content = json.dumps(page_content, ensure_ascii=False)
            documents.append(
                Document(
                    page_content=page_content,
                    metadata=metadata,
                )
            )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            separators=["}", "]", ",", "\n", "\n\n", "{", "["],
        )
        chunks = text_splitter.split_documents(documents)
        processed_chunked_docs = []
        for doc in chunks:
            text = doc.page_content
            text_length = len(text)
            if text_length <= max_chunk_size:
                # If chunk is within limit, keep it as is
                processed_chunked_docs.append(doc)
                continue
            # Document exceeds limit, split by character length
            logger.warning(
                f"Found chunk with {text_length} characters, "
                f"exceeding limit of {max_chunk_size}. Breaking into smaller chunks."
            )
            # Split into chunks of max_tokens characters
            for i in range(0, text_length, max_chunk_size):
                # Get the next chunk of text
                text_chunk = text[i : i + max_chunk_size]

                if text_chunk.strip():  # Only add non-empty chunks
                    new_doc = Document(
                        id=doc.id, page_content=text_chunk, metadata=doc.metadata.copy()
                    )
                    processed_chunked_docs.append(new_doc)
        # Add chunk_index and generate document ID
        for i, chunk in enumerate(processed_chunked_docs):
            chunk.metadata["chunk_index"] = i
            chunk.id = str(uuid4())
        return processed_chunked_docs

    @staticmethod
    def _character_split(
        text: str, max_chunk_size: int, overlap: int, filename: str | None = None
    ) -> list[Document]:
        """
        Split text by character count, avoiding word breaks.

        Args:
            text: The text to chunk
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of Document objects
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Find the end position for this chunk
            end = min(start + max_chunk_size, text_length)

            # Avoid cutting words in the middle (if not at the end of text)
            if end < text_length:
                # Find the last space before the end
                while end > start and text[end - 1] != " " and text[end] != " ":
                    end -= 1
                # If we couldn't find a good break point, just cut at max_chunk_size
                if end == start:
                    end = min(start + max_chunk_size, text_length)

            # Extract the chunk
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunk_index = len(chunks)
                metadata = {"chunk_index": chunk_index}
                if filename:
                    metadata["filename"] = filename
                doc = Document(
                    page_content=chunk,
                    metadata=metadata,
                    id=str(uuid4()),
                )
                chunks.append(doc)

            # Move the start position for the next chunk, accounting for overlap
            start = end - overlap
            if start < 0:
                start = 0

        return chunks

    @staticmethod
    def _sentence_split(
        text: str, max_chunk_size: int, overlap: int, filename: str | None = None
    ) -> list[Document]:
        """
        Split text by sentences using LangChain's RecursiveCharacterTextSplitter.

        Args:
            text: The text to chunk
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            separators=[". ", "! ", "? ", "\n", " ", ""],
        )

        text_chunks = text_splitter.split_text(text)
        docs = []
        for i, chunk in enumerate(text_chunks):
            metadata = {"chunk_index": i}
            if filename:
                metadata["filename"] = filename
            doc = Document(page_content=chunk, metadata=metadata, id=str(uuid4()))
            docs.append(doc)
        return docs

    @staticmethod
    def _paragraph_split(
        text: str, max_chunk_size: int, overlap: int, filename: str | None = None
    ) -> list[Document]:
        """
        Split text by paragraphs using LangChain's RecursiveCharacterTextSplitter.

        Args:
            text: The text to chunk
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        text_chunks = text_splitter.split_text(text)
        docs = []
        for i, chunk in enumerate(text_chunks):
            metadata = {"chunk_index": i}
            if filename:
                metadata["filename"] = filename
            doc = Document(page_content=chunk, metadata=metadata, id=str(uuid4()))
            docs.append(doc)
        return docs

    @staticmethod
    def _semantic_split(
        text: str, max_chunk_size: int, overlap: int, filename: str | None = None
    ) -> list[Document]:
        """
        Split text by semantic units using LangChain's RecursiveCharacterTextSplitter.

        This uses a more sophisticated recursive splitting approach that tries to keep
        related content together based on natural boundaries in the text.

        Args:
            text: The text to chunk
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of Document objects
        """
        text_splitter = RecursiveCharacterTextSplitter(
            # Define separators in order of priority
            separators=[
                "\n\n",  # Paragraphs first
                "\n",  # Then newlines
                ". ",  # Then sentences
                ", ",  # Then clauses
                " ",  # Then words
                "",  # Then characters
            ],
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            length_function=len,
        )

        text_chunks = text_splitter.split_text(text)
        docs = []
        for i, chunk in enumerate(text_chunks):
            metadata = {"chunk_index": i}
            if filename:
                metadata["filename"] = filename
            doc = Document(page_content=chunk, metadata=metadata, id=str(uuid4()))
            docs.append(doc)
        return docs
