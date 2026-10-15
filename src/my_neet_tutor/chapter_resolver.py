from pathlib import Path
import yaml
from my_neet_tutor.models import ChapterInfo

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHAPTERS_PATH = BASE_DIR/"config/chapters.yaml"
DOCUMENT_PATH = BASE_DIR/"data/documents/kebo101.pdf"

class_mapping= {
    "ke": "Class 11",
    "le": "Class 12"
}

subject_mapping = {
    "bo":"biology",
    "ch":"chemistry",
    "ph":"physics",
}


with open(CHAPTERS_PATH,"r",encoding="utf-8") as f:
    chapters = yaml.safe_load(f)

def resolve_chapter(document_path: Path) -> ChapterInfo:
    file_name = document_path.stem

    if len(file_name) < 6:
        raise ValueError(f"Filename too short: {file_name!r}")
    
    class_code,subject_code,part_number,chapter_number = file_name[0:2],file_name[2:4],file_name[4:5],file_name[5:]

    try:
        class_name = class_mapping[class_code]
        subject_name = subject_mapping[subject_code]
    except KeyError as e:
        raise ValueError(f"Unknown code {e} in filename {file_name!r}") from None


    chapter_key = f"{class_name.replace(' ','').lower()}-{subject_name}-ch{chapter_number}"

    try:
        chapter_name = chapters[chapter_key]
    except KeyError:
        raise ValueError(f"No chapter found for key {chapter_key!r}") from None

    return ChapterInfo(
        class_name=class_name,
        subject=subject_name,
        chapter_name=chapter_name,
    )

result = resolve_chapter(DOCUMENT_PATH)
print(result)