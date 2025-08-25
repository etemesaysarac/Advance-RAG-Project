from graph.chains.generation import generation_chain
#I imported the chain we created in generation.py into the generate.py file to use it.

def generate ():
    generation = generation_chain.invoke(
        {"context": "documents", "question": "question"}
    )