from sentence_transformers import SentenceTransformer
from my_neet_tutor.models import TextChunk

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    vector = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vector.tolist()


def generate_embeddings(
    chunks: list[TextChunk],
) -> list[list[float]]:
    texts = [chunk.text for chunk in chunks]

    if not texts:
        return []

    vectors = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return vectors.tolist()
