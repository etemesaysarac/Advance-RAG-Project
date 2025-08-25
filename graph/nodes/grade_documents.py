from typing import Any, Dict

from langchain_core.utils import print_text

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

    relevant_documents = []
    web_search = False

    for d in documents:
        score = retrival_grader.invoke(
            {"question": question, "documents": d.page_content}
            #I obtained the simplest form of the document with the page_content module.
        )

        grade = score.binary_score

        if grade.lower > "yes":
            #The result produced by "llm" can be in uppercase or lowercase. I want to see the entire result with ".lower" to see it for sure.
            print("---Grade : DOCUMENT RELEVANT TO QUESTION---")
            relevant_documents.append(d)
        else:
            print("---Grade : DOCUMENT NOT RELEVANT TO QUESTION---")
            web_search = True
            continue
        return {"question" : question, "documents" : relevant_documents, "web_search" : web_search}

    """
    relevant_documents = []
    I created an empty list called "relevant_documents." 
    I filtered the relevant information from the "for" loop and saved it to this list. 
    Then, I ensured that only relevant documents were returned in the "return" loop, preventing irrelevant documents from being constantly processed.
    """

