from typing import Any, Dict
from graph.state import GraphState
from ingestion import retriever

def retrieve(state : GraphState) -> Dict[str, Any]:
    print("----------RETRIEVE----------")

    question = state["question"]
    documents = retriever.invoke(question)

    return {"question": question, "documents": documents}
# I returned and saved the user and system outputs to save them and use them in nodes.