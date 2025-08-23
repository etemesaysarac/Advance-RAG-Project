from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

"""I'll check the data coming from router.py. I'll return a response asking if it's true or false. 
If it's true, I can move on to the next step, but if it's false, I'll go back to the previous step and ask docs to fix the error."""