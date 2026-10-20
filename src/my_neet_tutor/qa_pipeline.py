from my_neet_tutor.evidence_checker import evidence_check
from my_neet_tutor.models import RetrievedChunk, EvidenceCheck
from my_neet_tutor.vector_store import search_chunks

def check_question(
        question: str,
) -> tuple[list[RetrievedChunk],EvidenceCheck]:

    retrieved_chunks = search_chunks(question)

    evidence_result = evidence_check(question,retrieved_chunks)

    return retrieved_chunks, evidence_result