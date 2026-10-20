from langchain_groq import ChatGroq
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

def generate_structured_output(
    prompt: str,
    output_model: type[BaseModel],
) -> BaseModel:

    structured_llm = llm.with_structured_output(
        output_model,
        method="json_schema",
        strict=True,
    )

    return structured_llm.invoke(prompt)