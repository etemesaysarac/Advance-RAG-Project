from typing import Any, Dict
from graph.chains.retrieval_grader import retrival_grader
from graph.state import GraphState


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question.
    If any document is not relevant, we will set a flag to run web search.

    Args:
        state(dict) : The current state of the graph

    Returns:
        state(dict) : Filtered out irrelevant documents and updated web_search state
    """
    print("---CHECK DOCUMENT RELEVANT TO QUESTION---")

    question = state["question"]
    documents = state["documents"]

    web_search = False

    for d in documents:
        score = retrival_grader.invoke(
            {"question": question, "documents": d.page_content}
            #I obtained the simplest form of the document with the page_content module.
        )