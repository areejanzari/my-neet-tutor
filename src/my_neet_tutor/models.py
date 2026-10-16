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
    page_number: int = Field(ge=1,strict=True)
    metadata: dict = Field(default_factory=dict)

class ChapterInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    class_name: str = Field(min_length=1)
    subject: Literal["biology","physics","chemistry"]
    chapter_name: str = Field(min_length=1)