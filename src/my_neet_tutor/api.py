from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from my_neet_tutor.models import TutorResponse,ChatRequest
from my_neet_tutor.rag_pipeline import run_rag_pipeline
from my_neet_tutor.vector_store import get_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.collection = get_collection()
    print("My NEET Tutor started!")
    yield

    print("My NEET Tutor is shutting down!")

app = FastAPI(
    title="My Neet Tutor API",
    description="A textbook-grounded question-answering API.",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get('/health')
def health_check() -> dict[str,str]:
    return {"status": "ok"}

@app.post('/chat',response_model=TutorResponse)
def chat(request: ChatRequest) -> TutorResponse:
    try:
        return run_rag_pipeline(request.question,
                                collection=app.state.collection,)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc