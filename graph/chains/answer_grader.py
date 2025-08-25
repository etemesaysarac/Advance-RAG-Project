from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.chains.retrieval_grader import system_prompt


class GraderAnswer(BaseModel):

    binary_score: str Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatOpenAI(temperature=0)
structred_llm_grader = llm.structred_llm_grader(GraderAnswer)

system_prompt = """
You are a grader assessing wheter an answer addresses / resolves a question. \n
Give a binary score 'yes' or 'no'. 'Yes' means that answer resolves the question. 
"""

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "User question: \n\n {question}\n\n LLM generation: {generation")
])
