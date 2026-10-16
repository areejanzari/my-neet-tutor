from pathlib import Path
from unstructured.partition.pdf import partition_pdf

def extract_elements(document_path: Path):

    elements = partition_pdf(
        filename=str(document_path),
        strategy="hi_res",
        infer_table_structure=True,
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        languages=["eng"]
    )

    return elements

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# DOCUMENT_PATH = BASE_DIR/"data/documents/kebo101.pdf"
# elements = extract_elements(DOCUMENT_PATH)
# print(f"Extracted {len(elements)} elements")

