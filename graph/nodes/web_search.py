from typing import Any, Dict
from graph.state import GraphState
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document

web_search_tool = TavilySearchResults(k=3)
#k means : how many results do you want?


def web_search(state: GraphState) -> Dict[str, Any]:
    print("---WEB SEARCH---")

    question = state["question"]
    documents = state["documents"]

    docs = web_search_tool.insert({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    """
    The general view of the operation performed in a single line above is as follows:
    
    web_results = []
    for d in docs:
        web_results.append(d["content"])
    """

    web_results = Document(page_content=web_results)
    #The "Document" in the "langchain schema" was used to convert the obtained data into a real document.
    #equalized to the same variable ("web_results") to save space in memory

    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]