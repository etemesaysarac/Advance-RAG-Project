`graph/chains/README.md`

````md
# graph/chains — Router, Graders & Generation Chains

**Purpose (short):**
This folder contains the LLM-driven *runnable chains* that implement the decision logic used by the LangGraph orchestration. Chains provide deterministic, structured outputs (Pydantic models) used by the graph to route queries, assess document relevance, check for hallucinations, and validate whether a generated answer actually addresses the user’s question.

> Audience: engineers implementing or extending graders / prompt logic; researchers evaluating chain performance.

---

## Contents (files)
| File | Responsibility (high level) |
|---|---|
| `router.py` | Classify incoming questions to a datasource (`vectorstore` or `websearch`). Exposes `question_router`. |
| `retrieval_grader.py` | Assess whether an individual retrieved document is relevant to a question. Exposes `retrieval_grader`. |
| `hallucination_grader.py` | Determine whether the LLM’s generation is grounded in the provided documents. Exposes `hallucination_grader`. |
| `answer_grader.py` | Evaluate whether the LLM’s generation answers the question. Exposes `answer_grader`. |
| `generation.py` | Pulls prompt template (`rlm/rag-prompt`) from LangChain Hub and pipes into ChatOpenAI. Exposes `generation_chain`. |

---

## Architectural diagram (visual)
<p align="center">
  <img src="../../Assets/LANGRAPH_structure.png" alt="LangGraph chains architecture" style="max-width:100%;height:auto"/>
</p>

*Figure — LangGraph: router, graders, and generation chain (high-level).*

---

## Output schemas (structured models)
All chains return **structured outputs** built with Pydantic (or LangChain pydantic wrapper). Structured outputs ensure deterministic parsing and eliminate ad-hoc string parsing.

### Router model (from `router.py`)
```py
from typing import Literal
from pydantic import BaseModel, Field

class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "websearch"] = Field(..., description="Route target")
````

### Retrieval grader (from `retrieval_grader.py`)

```py
from pydantic import BaseModel, Field

class GradeDocuments(BaseModel):
    # returns 'yes' or 'no' (string) in current implementation
    binary_score: str = Field(description="Documents relevant? 'yes' | 'no'")
```

### Hallucination grader (from `hallucination_grader.py`)

```py
from pydantic import BaseModel, Field

class GradeHallucinations(BaseModel):
    binary_score: bool = Field(description="Generation grounded in documents? True/False")
```

### Answer grader (from `answer_grader.py`)

```py
from pydantic import BaseModel, Field

class GraderAnswer(BaseModel):
    binary_score: bool = Field(description="Does generation address question? True/False")
```

---

## Prompts & Intent descriptions (implementation-level)

Below are the canonical prompt intents implemented. Keep system prompts terse and unambiguous.

1. **Router system prompt** (`router.py`) — *intent:* classify whether the question is in-domain for local index (vectorstore) or requires web search.

   ```
   System: You are an expert at routing a user question to a vectorstore or web search.
   The vectorstore contains documents related to agents, prompt engineering and adversarial attack on LLMs.
   Use the vectorstore for questions on these topics. For all else, use web search.
   ```

2. **Retrieval grader system prompt** (`retrieval_grader.py`) — *intent:* is this retrieved doc semantically relevant?

   ```
   System: You are a grader assessing relevance of a retrieved document to a user question.
   If the document contains keyword(s) or semantic meaning related to the question, grade 'yes', otherwise 'no'.
   ```

3. **Hallucination grader system prompt** (`hallucination_grader.py`) — *intent:* is the generation supported by the set of facts?

   ```
   System: You are a grader assessing whether an LLM generation is grounded in/support by a set of retrieved facts.
   Give boolean True/False (True => grounded).
   ```

4. **Answer grader system prompt** (`answer_grader.py`) — *intent:* does the generation resolve the user’s question?

   ```
   System: You are a grader assessing whether an answer addresses / resolves a question.
   Return boolean True/False.
   ```

> **Implementation note:** all graders set `temperature=0` and are used via `llm.with_structured_output(Model)` to enforce typed outputs.

---

## Usage examples (snippets)

### Router

```py
from graph.chains.router import question_router
out = question_router.invoke({"question": "How to build an LLM agent?"})
# out.datasource -> 'vectorstore'  (expected if topics are in the index)
```

### Retrieval grader

```py
from graph.chains.retrieval_grader import retrieval_grader
res = retrieval_grader.invoke({"question": "What is prompt engineering?", "document": doc_text})
# res.binary_score -> 'yes' or 'no'
```

### Hallucination grader

```py
from graph.chains.hallucination_grader import hallucination_grader
res = hallucination_grader.invoke({"documents": [doc1, doc2], "generation": generated_text})
# res.binary_score -> True/False
```

### Generation chain

```py
from graph.chains.generation import generation_chain
ans = generation_chain.invoke({"context": [p1, p2], "question": q})
# ans -> string (StrOutputParser)
```

---

## Evaluation & metrics

To evaluate chain performance maintain a small labeled dataset and collect these metrics:

| Metric                             |                                   Description | Where to compute                          |
| ---------------------------------- | --------------------------------------------: | ----------------------------------------- |
| Router accuracy                    |          fraction of queries correctly routed | router unit tests                         |
| Retrieval relevance (precision\@k) |     proportion of retrieved passages relevant | retrieval grader + human labels           |
| Hallucination rate                 |        fraction of answers judged unsupported | hallucination grader + human verification |
| Answer accuracy                    | fraction of answers that resolve the question | answer grader + gold answers              |

Recommended: run a nightly job that samples N queries and computes these metrics, storing results in a CSV or a lightweight dashboard.

---

## Best practices & engineering notes

* **Schema-first**: prefer `with_structured_output` and BaseModel outputs for all chains. Do not parse free text.
* **Determinism**: keep `temperature=0` for graders; use `temperature` > 0 only for creative generation nodes if necessary.
* **Token budget**: pass only top-k passages to the hallucination grader (e.g. top 3), otherwise you risk exceeding model context windows.
* **Idempotent prompts**: avoid context that encourages the model to elaborate; force short schema-conforming answers.
* **Prompts versioning**: store the exact system/human prompt strings (or prompt IDs) in a `prompts/` folder or in source as constants; record which prompt version was used in logs.

---

## Testability & mocking

* Use `monkeypatch` to replace chain `.invoke()` with deterministic returns in unit tests. Example:

```py
def test_router(monkeypatch):
    class Dummy:
        def invoke(self, x): return RouteQuery(datasource='vectorstore')
    monkeypatch.setattr("graph.chains.router.question_router", Dummy())
    ...
```

* Add small integration tests that compose router → retrieve (mocked) → grader in CI.

---

## Troubleshooting (common failure modes)

* **Non-conforming outputs:** If `with_structured_output` fails to parse, examine the raw LLM output in traces. LangChain tracing helps.
* **Latency / rate limits:** graders call LLMs; consider batch evaluation or async execution to reduce wall-clock time during tests.
* **Ambiguous router decisions:** add more explicit rules in system prompt, or add fallback rules in `route_question` logic.

---

## Maintenance

* When adding a new chain, update this README with model schema, sample prompt, and tests.
* Keep prompt text under version control and record LangChain/ChatOpenAI versions in `requirements.txt`.

