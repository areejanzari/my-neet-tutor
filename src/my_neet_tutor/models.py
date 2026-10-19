from pydantic import BaseModel,Field,ConfigDict
from typing import Literal

class DocumentElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    element_type: Literal["text", "table"]
    category: Literal[
        "UncategorizedText",
        "NarrativeText",
        "ListItem",
        "Table"
    ]
    element_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    page_number: int = Field(ge=1, strict=True)
    metadata: dict = Field(default_factory=dict)

class ChapterInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    class_name: str = Field(min_length=1)
    subject: Literal["biology","physics","chemistry"]
    chapter_name: str = Field(min_length=1)

class TextChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    page_start: int = Field(ge=1, strict=True)
    page_end: int = Field(ge=1, strict=True)
    element_ids: list[str] = Field(min_length=1)
    piece_ids: list[str]
