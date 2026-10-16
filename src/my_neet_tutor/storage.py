import json
from pathlib import Path

def write_json(data: list | dict, file_path: Path) -> None:
    with file_path.open("w",encoding="utf-8") as file:
        json.dump(data,file,indent=2,ensure_ascii=False)

def save_processed_data(
        elements_data: list[dict],
        content_data: dict,
        output_dir: Path,
    ) -> None:

    metadata_ids = {item["element_id"] for item in elements_data}
    content_ids = set(content_data.keys())

    if metadata_ids != content_ids:
        raise ValueError("Metadata and content IDs do not match.")

    output_dir.mkdir(parents=True,exist_ok=True)

    elements_temp = output_dir / "elements.tmp.json"
    content_temp = output_dir / "content.tmp.json"

    elements_path = output_dir / "elements.json"
    content_path = output_dir / "content.json"

    write_json(elements_data, elements_temp)
    write_json(content_data, content_temp)

    elements_temp.replace(elements_path)
    content_temp.replace(content_path)

    