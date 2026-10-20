from pathlib import Path
from my_neet_tutor.models import ChapterInfo
from my_neet_tutor.extraction import extract_elements
from my_neet_tutor.storage import save_processed_data
from my_neet_tutor.chapter_resolver import resolve_chapter

def transform_elements(
    elements,
    document_id: str,
    chapter_info: ChapterInfo,
) -> tuple[list[dict], dict]:
    elements_data = []
    content_data = {}

    for element in elements:
        element_dict = element.to_dict()
        metadata = element_dict.get("metadata", {})
        element_id = element_dict["element_id"]

        elements_data.append({
            "element_id": element_id,
            "element_type": (
                "table" if element_dict["type"] == "Table" else "text"
            ),
            "category": element_dict["type"],
            "document_id": document_id,
            "chapter_name": chapter_info.chapter_name,
            "page_number": metadata.get("page_number"),
        })

        content_data[element_id] = {
            "text": element_dict.get("text", ""),
            "html": metadata.get("text_as_html"),
        }

    return elements_data, content_data


def ingest_document(
    document_path: Path,
    chapter_info: ChapterInfo,
) -> None:
    if not document_path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {document_path}"
        )

    if document_path.suffix.lower() != ".pdf":
        raise ValueError(
            "The document must be a PDF file."
        )

    elements = extract_elements(document_path)
    elements_data, content_data = transform_elements(
        elements=elements,
        document_id=document_path.stem,
        chapter_info=chapter_info,
    )

    output_dir = (
        document_path.parent.parent
        / "processed"
        / document_path.stem
    )

    save_processed_data(
        elements_data=elements_data,
        content_data=content_data,
        output_dir=output_dir,
    )

    print(f"Saved {len(elements_data)} elements to {output_dir}")