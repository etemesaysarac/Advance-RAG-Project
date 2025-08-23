from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.pydantic_v1 import BaseModel, Field   old usage
from pydantic import BaseModel, Field
from typing import Literal


"""from dotenv import load_dotenv
load_dotenv()"""


class RouteQuery(BaseModel):
    """
    Route a user query to the most relevant datasource.
    """
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore"
    )

llm = ChatOpenAI(temperature=0)
#I dont want ChatGPT to be hallucinated! So, temperature must be about zero.
structured_llm_router = llm.with_structured_output(RouteQuery)
# "llm" and "RouteQuery" are linked. This way, the returned response will be one of the options specified in Literal.

system_prompt= """
You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering and adversarial attack on llms.
Use the vectorstore for question on these topics. For all else, use web search.
"""

route_prompt =ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{question}")
    ])

question_router = route_prompt | structured_llm_router
#I created a chain called "question_router" to receive and process data from the system and the user.

"""
if __name__ == '__main__':
    print(question_router.invoke(
        {"question": "How can I make hamburger?"}
    ))
#When asked "What is agent on llm?", he responded "vectorstore." The program works efficiently."""