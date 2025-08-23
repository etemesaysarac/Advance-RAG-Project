from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.pydantic_v1 import BaseModel, Field   old usage
from pydantic import BaseModel, Field
from typing import Literal


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


if __name__ == '__main__':
    print("Hi")


