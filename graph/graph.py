from graph.node_constants import RETRIEVE, GENERATE, WEBSEARCH, GRADE_DOCUMENTS
from graph.nodes import generate, grade_documents, web_search, retrieve
from graph.chains.router import question_router, RouteQuery
from graph.state import GraphState
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.answer_grader import answer_grader
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv

load_dotenv()


workflow = StateGraph(GraphState)

