from __future__ import annotations

from enum import Enum, auto

from pydantic import BaseModel, Field


class SplitterType(str, Enum):
    """Supported strategies for splitting raw content into chunks."""

    JSON = auto()
    CHARACTER = auto()
    SENTENCE = auto()
    PARAGRAPH = auto()


class ChunkerConfig(BaseModel):
    """Configuration options that control chunk generation."""

    splitter: SplitterType = Field(
        default=SplitterType.SENTENCE,
        description="Chunking strategy to apply to incoming content.",
    )
    chunk_size: int = Field(
        default=500,
        description="Maximum number of characters per chunk.",
    )
    chunk_overlap: int = Field(
        default=100,
        description="Number of overlapping characters between consecutive chunks.",
    )
