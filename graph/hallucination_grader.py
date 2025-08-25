from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

llm = ChatOpenAI(temperature=0)

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generated answer."""

    binary_score: str =Field(
        description="TAnswer is gounded in the facts, 'yes' or 'no'",
    )