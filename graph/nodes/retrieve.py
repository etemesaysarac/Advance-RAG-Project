from typing import Any, Dict
from graph.state import GraphState
from ingestion import retriver

def retrieve(state : GraphState) -> Dict[str, Any]:
    print("----------RETRIVE----------")

    question = state["question"]
    documents = retriver.invoke(question)

    return {"question": question, "documents": documents}
# I returned and saved the user and system outputs to save them and use them in nodes.