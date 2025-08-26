
## `graph/nodes/README.md`

```md
# graph/nodes — Node Reference, I/O Contracts & Implementation Notes

**Purpose (short):**
This folder contains the *executable nodes* used by the LangGraph StateGraph. Each node is a function that accepts the shared `GraphState` and returns the fields it updates. Nodes encapsulate concrete business logic: retrieval from vector store, document grading, web search enrichment, and LLM-based generation.

> Audience: implementers extending node behavior, QA engineers writing contract tests, and maintainers documenting data provenance.

---

## Contents & responsibilities
| File | Primary responsibility | Key side-effects |
|---|---|---|
| `__init__.py` | Re-export nodes for `graph.graph` imports | none |
| `retrieve.py` | Query the Chroma retriever to fetch context passages | reads `.chroma` persistent store |
| `grade_documents.py` | Use `retrieval_grader` chain to filter retrieved docs and set `web_search` flag | calls LLM grader; may set `web_search=True` |
| `web_search.py` | Query external web (Tavily) and append results to `documents` | network I/O; should write `Document.metadata['source']` |
| `generate.py` | Invoke `generation_chain` to produce `generation` string | calls LLM; may produce citations (pending) |

---

## Node I/O contract (GraphState)
```py
# graph/state.py (canonical shape)
from typing import List, TypedDict
from langchain.schema import Document

class GraphState(TypedDict):
    question: str
    generation: str            # produced by generate.py
    web_search: bool           # grade_documents may set to True
    documents: List[Document]  # LangChain Document objects (retriever + web results)
````

**Node behaviour convention**

* Nodes **read** fields they need (usually `question`, `documents`) and **return** a dict containing only the fields they update.
* Do **not** mutate the passed `state` in-place. Return a fresh dict.

---

## Implementation details & examples

### `retrieve.py`

**Purpose:** call the configured retriever (Chroma) for the query.

**Key code pattern (current):**

```py
from ingestion import retriever   # current approach

def retrieve(state: GraphState) -> Dict[str, Any]:
    q = state["question"]
    documents = retriever.invoke(q)
    return {"question": q, "documents": documents}
```

**Recommendation:** refactor to a factory:

```py
def get_retriever(config) -> Retriever:
    # returns configured Chroma retriever
```

So `retrieve.py` calls `get_retriever()` rather than importing `ingestion.retriever` at module load time.

---

### `grade_documents.py`

**Purpose:** determine relevance of each retrieved `Document` via `retrieval_grader`.

**Behavioral contract:**

* Input: `question`, `documents` (list)
* Action: call `retrieval_grader.invoke({"question": question, "document": d.page_content})`
* If `binary_score` == `'yes'` → retain doc; else set `web_search = True`.
* Output: `documents` (filtered), `web_search` (bool)

**Edge cases to handle:**

* Empty `documents` list → set `web_search = True` and return empty list.
* API errors from grader → retry with backoff or set `web_search = True` as safe fallback.

---

### `web_search.py`

**Purpose:** supplement the graph’s context using Tavily results.

**Current design (from code):**

* Calls `TavilySearchResults(k=3).invoke({"query": question})`
* Joins result content into a **single** `Document` and appends it.

**Recommendation (strong):**

* Do **not** concatenate results into one Document. Instead:

```py
results = web_search_tool.invoke({"query": question})
docs = [Document(page_content=res["content"], metadata={"source": res.get("url")}) for res in results]
documents.extend(docs)
```

* This allows per-document grading and fine-grained citation.

---

### `generate.py`

**Purpose:** produce final answer using `generation_chain`.

**Current pattern:**

```py
generation = generation_chain.invoke({"context": documents, "question": question})
return {"documents": documents, "question": question, "generation": generation}
```

**Recommendations:**

* Prefer returning a structured generation object:

```py
{"generation": {"text": text, "citations": [...], "model": "gpt-4o"}}
```

* If `generation_chain` cannot produce citations, add a post-processing step to convert inline URL references into structured metadata.

---

## Logging, provenance & metadata

* Enforce `Document.metadata` keys: `{"source": str, "retriever_score": float, "retriever_id": str, "timestamp": iso}`.
* Persist a trace id across nodes: `trace_id = uuid4()` set at entry and propagate via `Document.metadata['trace_id']`.

---

## Error handling patterns

* For external calls (Chroma, Tavily, OpenAI): use `tenacity` with exponential backoff. Example wrapper:

```py
@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def safe_invoke(chain, args):
    return chain.invoke(args)
```

* If retriever fails, fall back to `web_search=True` and continue the graph (fail-open policy for availability).

---

## Tests & examples

### Node unit test example (pytest)

```py
# tests/test_nodes.py

def test_generate_contract(monkeypatch):
    class DummyGen:
        def invoke(self, args): return "dummy-answer"
    monkeypatch.setattr('graph.chains.generation.generation_chain', DummyGen())
    state = {"question":"q","generation":"","web_search":False,"documents":[]}
    from graph.nodes.generate import generate
    out = generate(state)
    assert 'generation' in out and isinstance(out['generation'], str)
```

### Integration smoke test

* Compose a test that:

  1. Runs `ingestion.py` to build a small local index (or use a fixture index).
  2. Invokes `graph.graph.app.invoke({"question": "sample"})`.
  3. Asserts final state contains `generation` and `documents`.

---

## Best practices & maintenance checklist

* **Keep `state.py` authoritative**. Any change to the GraphState must be followed by corresponding README updates and tests.
* **Document metadata schema** in `graph/README.md` and enforce it with tests.
* **Do not import retriever at module top-level** (causes startup/order issues); use factory or lazy init.
* **Add smoke tests** that run in CI using mocked LLMs or a small test token (avoid leaking secrets).
* **Version prompts**: keep each chain’s prompt string in code and maintain a `PROMPT_VERSION` constant.

---

## Visual quick-reference (flow)

<p align="center">
  <img src="../../Assets/graph.png" alt="High-level node flow (Retrieve → Grade → Generate → (Web Search))" style="max-width:100%;height:auto" />
</p>

*Figure — Node-level flow: retrieval, document grading, generation, and optional web search enrichment.*

---

## Appendix: Example return shapes

* **retrieve.py** → `{"documents": [Document, ...], "question": q}`
* **grade\_documents.py** → `{"documents": filtered_docs, "question": q, "web_search": bool}`
* **web\_search.py** → `{"documents": enriched_docs, "question": q}`
* **generate.py** → `{"generation": "text", "documents": docs, "question": q}`

---

```

---

### Instructions

The two README blocks above are ready to paste into their respective folders. Open the canvas document, copy the exact block for `graph/chains/README.md` into `graph/chains/README.md` and the block for `graph/nodes/README.md` into `graph/nodes/README.md` in PyCharm.

If you want, I can now prepare a single commit patch to add these files to your repository — tell me the commit message and branch (default `main`) and I will prepare it.

```
