from pathlib import Path
import chromadb
from chromadb.api.models.Collection import Collection
from my_neet_tutor.embeddings import generate_embedding
from my_neet_tutor.models import RetrievedChunk, TextChunk


CHROMA_DIR = Path("data/chroma")
COLLECTION_NAME = "neet_chunks"


def get_collection() -> Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def store_chunks(
    chunks: list[TextChunk],
    vectors: list[list[float]],
) -> None:
    if len(chunks) != len(vectors):
        raise ValueError("The number of chunks and vectors must match.")

    if not chunks:
        return

    collection = get_collection()

    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=vectors,
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {
                "document_id": chunk.document_id,
                "chapter_name": chunk.chapter_name,
                "page_numbers": chunk.page_numbers,
            }
            for chunk in chunks
        ],
    )


def search_chunks(
    question: str,
    collection: Collection | None = None,
    top_k: int = 4,
) -> list[RetrievedChunk]:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if collection is None:
        collection = get_collection()

    if collection.count() == 0:
        return []

    query_vector = generate_embedding(question)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for i, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i]

        matches.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                text=results["documents"][0][i],
                document_id=metadata["document_id"],
                chapter_name=metadata["chapter_name"],
                page_numbers=metadata["page_numbers"],
                distance=results["distances"][0][i],
            )
        )

    return matches
