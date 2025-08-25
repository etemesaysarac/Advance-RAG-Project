from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class GraderAnswer(BaseModel):

    binary_score: str Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatOpenAI(temperature=0)
structred_llm_grader = llm.structred_llm_grader(GraderAnswer)
