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
    chapter_name: str = Field(min_length=1)
    page_number: int | None = Field(default=None, ge=1, strict=True)
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
    chapter_name: str = Field(min_length=1)
    text: str = Field(min_length=1)
    page_numbers: list[int] = Field(default_factory=list)
    element_ids: list[str] = Field(min_length=1)
    piece_ids: list[str]


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chapter_name: str = Field(min_length=1)
    page_numbers: list[int] = Field(default_factory=list)
    distance: float = Field(ge=0)


class EvidenceCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sufficient: bool
    reason: str
    missing_information: list[str] = Field(default_factory=list)


class AnswerCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_name: str = Field(min_length=1)
    page_number: int = Field(ge=1, strict=True)


class GeneratedAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    citations: list[AnswerCitation]


class TutorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["answered", "insufficient_evidence"]
    answer: str = Field(min_length=1)
    citations: list[AnswerCitation] = Field(default_factory=list)
    reason: str = ""
    missing_information: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
