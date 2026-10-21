from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from chromadb.api.models.Collection import Collection
from my_neet_tutor.answer_generator import generate_answer
from my_neet_tutor.evidence_checker import evidence_check
from my_neet_tutor.models import EvidenceCheck, RetrievedChunk, TutorResponse
from my_neet_tutor.vector_store import search_chunks

class RAGState(TypedDict,total=False):
    question: str
    retrieved_chunks: list[RetrievedChunk]
    evidence_check: EvidenceCheck
    response: TutorResponse
    collection: Collection | None

def retrieve_node(state: RAGState) -> dict:
    chunks = search_chunks(
        question=state['question'],
        collection=state.get("collection"),
        top_k=4,
    )

    return {"retrieved_chunks": chunks}

def evidence_check_node(state: RAGState) -> dict:
    result = evidence_check(
        question=state['question'],
        retrieved_chunks=state["retrieved_chunks"],
    )

    return {"evidence_check": result}

def route_after_evidence(
        state: RAGState
        ) -> Literal["generate_answer", "insufficient_evidence"]:
    
    if state["evidence_check"].sufficient:
        return "generate_answer"
    
    return "insufficient_evidence"

def generate_answer_node(state: RAGState) -> dict:
    check = state["evidence_check"]

    generated = generate_answer(
        question=state["question"],
        retrieved_chunks=state["retrieved_chunks"],
        missing_information=check.missing_information,
    )

    response = TutorResponse(
        status="answered",
        answer=generated.answer,
        citations=generated.citations,
        missing_information=check.missing_information,
    )

    return {"response": response}

def insufficient_evidence_node(state: RAGState) -> dict:
    check = state["evidence_check"]

    missing = check.missing_information

    answer = "I couldn't find enough supporting evidence in the retrieved textbook passages to answer this question reliably."

    if missing:
        answer += " Information not established by the evidence: " + "; ".join(missing) + "."

    response = TutorResponse(
        status="insufficient_evidence",
        answer=answer,
        citations=[],
        reason=check.reason,
        missing_information=missing,
    )

    return {"response": response}

graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("check_evidence", evidence_check_node)
graph.add_node("generate_answer", generate_answer_node)
graph.add_node("insufficient_evidence", insufficient_evidence_node)

graph.add_edge(START,"retrieve")
graph.add_edge("retrieve","check_evidence")

graph.add_conditional_edges(
    "check_evidence",
    route_after_evidence,
    {
        "generate_answer": "generate_answer",
        "insufficient_evidence": "insufficient_evidence"
    },
)
graph.add_edge("generate_answer", END)
graph.add_edge("insufficient_evidence", END)

rag_graph = graph.compile()


def run_rag_pipeline(
    question: str,
    collection: Collection | None = None,
) -> TutorResponse:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    result = rag_graph.invoke({
        "question": question,
        "collection": collection,
    })

    return result["response"]

