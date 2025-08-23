from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.chains.router import structured_llm_router

"""I'll check the data coming from router.py. I'll return a response asking if it's true or false. 
If it's true, I can move on to the next step, but if it's false, I'll go back to the previous step and ask docs to fix the error."""

llm = ChatOpenAI(temperature=0)
#I dont want GPT to be hallucinated!

class GradeDocuments(BaseModel):
    """Binary scrore for relevance check on retrieved documents"""

    binary_score: str =Field(
        description="Documents are relevant to the question, 'yes' or 'no'",
    )

structured_llm_grader = llm.with_structured_output(GradeDocuments)
#I wrote nearly same code at router.py

system_prompt = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

grade_promt = ChatPromptTemplate.from_messages(
    [("system": system_prompt),
     ("human"): "Retrieved document : {document}, User question : {question}")
])
#The system was told: What is the relationship between the question and the document?

