from typing import Dict, Any
from graph.chains.generation import generation_chain
from graph.state import GraphState


#I imported the chain we created in generation.py into the generate.py file to use it.

def generate (state : GraphState) -> Dict[str, Any]:
    print("----------GENERATE----------")
    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke(
        {"context": "documents", "question": "question"}
    )

    return {"generation": generation, "question": question, "documents": documents}
# I returned and saved the user and system outputs to save them and use them in nodes.