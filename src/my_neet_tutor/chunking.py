import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from transformers import AutoTokenizer
from my_neet_tutor.models import DocumentElement, TextChunk


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)


def table_to_records(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if table is None:
        return []

    headers = [
        " ".join(header.get_text(" ", strip=True).split())
        for header in table.select("thead th")
    ]

    records = []

    for row in table.select("tbody tr"):
        cells = [
            cell.get_text(" ", strip=True)
            for cell in row.find_all("td")
        ]

        if not headers or len(cells) != len(headers):
            continue

        record = "\n".join(
            f"{header}: {value}"
            for header, value in zip(headers, cells)
        )
        records.append(record)

    return records


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_text(
    text: str,
    max_tokens: int = 200,
    overlap: int = 50,
) -> list[str]:
    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
        truncation=False,
        verbose=False,
    )

    chunks = []
    start = 0

    while start < len(token_ids):
        end = start + max_tokens
        chunk_tokens = token_ids[start:end]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True,
        )
        chunks.append(chunk_text)

        if end >= len(token_ids):
            break

        start = end - overlap

    return chunks


def split_large_elements(
    elements: list[dict],
    max_tokens: int = 200,
    overlap: int = 50,
) -> list[dict]:
    result = []

    for element in elements:
        if count_tokens(element["text"]) <= max_tokens:
            result.append(element)
            continue

        pieces = split_text(
            element["text"],
            max_tokens=max_tokens,
            overlap=overlap,
        )

        for piece_number, piece in enumerate(pieces, start=1):
            split_element = element.copy()
            split_element["text"] = piece
            split_element["piece_id"] = (
                f"{element['element_id']}_piece_{piece_number}"
            )
            result.append(split_element)

    return result


def is_page_furniture(text: str) -> bool:
    text = text.strip()

    if re.fullmatch(r"\d+", text):
        return True

    if re.fullmatch(
        r"Reprint\s+\d{4}-\d{2}",
        text,
        re.IGNORECASE,
    ):
        return True

    return False


def load_elements(data_dir: Path) -> list[dict]:
    with (data_dir / "elements.json").open(encoding="utf-8") as file:
        elements = json.load(file)

    with (data_dir / "content.json").open(encoding="utf-8") as file:
        content = json.load(file)

    result = []

    supported_categories = {
        "UncategorizedText",
        "NarrativeText",
        "ListItem",
        "Table",
    }

    skipped_count = 0

    for raw_element in elements:
        if raw_element.get("category") not in supported_categories:
            skipped_count += 1
            continue

        element = DocumentElement.model_validate(raw_element)

        element_id = element.element_id
        item = content.get(element_id)

        if item is None:
            raise ValueError(
                f"No content found for element {element_id!r}"
            )

        if element.category == "Table":
            records = table_to_records(item.get("html") or "")

            if records:
                for row_number, record in enumerate(records, start=1):
                    if not record.strip():
                        continue

                    row_element = element.model_dump()
                    row_element["element_id"] = (
                        f"{element_id}_row_{row_number}"
                    )
                    row_element["source_element_id"] = element_id
                    row_element["text"] = record
                    result.append(row_element)

                continue

        # plain text for non-table elements and as a table fallback.
        text = item.get("text", "")

        if not text.strip() or is_page_furniture(text):
            continue

        loaded_element = element.model_dump()
        loaded_element["source_element_id"] = element_id
        loaded_element["text"] = text
        result.append(loaded_element)

    if skipped_count:
        print(f"Skipped {skipped_count} unsupported elements.")

    return result


def combine_text(elements: list[dict]) -> str:
    return "\n\n".join(
        element["text"].strip()
        for element in elements
        if element["text"].strip()
    )


def fits_in_chunk(
    elements: list[dict],
    next_element: dict,
    max_tokens: int = 200,
) -> bool:
    candidate = elements + [next_element]
    candidate_text = combine_text(candidate)
    return count_tokens(candidate_text) <= max_tokens


def create_chunk(
    elements: list[dict],
    chunk_number: int,
) -> TextChunk:
    page_numbers = sorted({
        element["page_number"]
        for element in elements
        if element.get("page_number") is not None
    })

    document_ids = {
        element["document_id"]
        for element in elements
    }

    chapter_names = {
        element["chapter_name"]
        for element in elements
    }

    if len(document_ids) != 1:
        raise ValueError("A chunk cannot contain multiple documents.")

    if len(chapter_names) != 1:
        raise ValueError("A chunk cannot contain multiple chapters.")

    return TextChunk(
        chunk_id=(
            f"{elements[0]['document_id']}__chunk_{chunk_number:04d}"
        ),
        document_id=elements[0]["document_id"],
        chapter_name=elements[0]["chapter_name"],
        text=combine_text(elements),
        page_numbers=page_numbers,
        element_ids=[
            element["element_id"]
            for element in elements
        ],
        piece_ids=[
            element.get("piece_id", element["element_id"])
            for element in elements
        ],
    )


def build_chunks(
    elements: list[dict],
    max_tokens: int = 200,
) -> list[TextChunk]:
    elements = split_large_elements(
        elements,
        max_tokens=max_tokens,
    )

    chunks = []
    current_elements = []

    for element in elements:
        if not current_elements:
            current_elements.append(element)
            continue

        current_has_unknown_page = (
            current_elements[0].get("page_number") is None
        )
        next_has_unknown_page = (
            element.get("page_number") is None
        )

        if current_has_unknown_page != next_has_unknown_page:
            chunks.append(
                create_chunk(current_elements, len(chunks) + 1)
            )
            current_elements = [element]
            continue

        if fits_in_chunk(current_elements, element, max_tokens):
            current_elements.append(element)
        else:
            chunks.append(
                create_chunk(current_elements, len(chunks) + 1)
            )
            current_elements = [element]

    if current_elements:
        chunks.append(
            create_chunk(current_elements, len(chunks) + 1)
        )

    return chunks
