from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from graph.chains.hallucination_grader import structured_llm_grader
from graph.chains.retrieval_grader import system_prompt

class GraderAnswer(BaseModel):

    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatOpenAI(temperature=0)
structred_llm_grader = llm.with_structured_output(GraderAnswer)

system_prompt = """
You are a grader assessing wheter an answer addresses / resolves a question. \n
Give a binary score 'yes' or 'no'. 'Yes' means that answer resolves the question. 
"""

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "User question: \n\n {question}\n\n LLM generation: {generation}")
])

answer_grader : RunnableSequence = answer_prompt | structured_llm_grader

"""
In answer_prompt, the question (the actual question asked by the user)-generation (LLM output) relationship was checked.
In hallucination_grader.py, the document (user data)-generation (LLM output) relationship was checked.
In retrieval_grader.py, the document-question relationship was checked.

Thus, all possibilities are checked by the LLM.
"""
