# LearningAgent Agent Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade LearningAgent into a resume-ready modern AI Agent project with MCP integration, multi-scope long-term memory, hybrid retrieval, agent tracing/evaluation, and adaptive learning feedback.

**Architecture:** Keep the current three-layer architecture: `MainAgent` as coordinator, task agents/processors as functional layer, and specialist agents as domain tools. Add cross-cutting infrastructure for memory, retrieval, tracing, evaluation, and MCP exposure without rewriting existing CLI flows.

**Tech Stack:** Python 3.10+, HelloAgents, pytest, scikit-learn, sentence-transformers, FAISS, Markdown file storage, optional MCP Python SDK.

---

## 1. Current Baseline

LearningAgent already has a solid foundation:

- `core/main_agent.py` routes user intent to feature modules.
- `agents/create_plan_agent.py` creates learning plans from domain text, GitHub repositories, or PDF papers.
- `processors/add_knowledge.py` stores notes and updates summaries.
- `agents/vibe_learning_agent.py` supports free-form learning and quiz sessions.
- `agents/summary_agent.py` generates progress reports from plans, notes, and sessions.
- `core/memory_conflict_resolver.py`, `core/memory_compressor.py`, and `core/memory_hierarchy.py` provide early memory-system foundations.
- `tests/` already contains unit and integration tests.

The upgrade should build on this instead of replacing it.

---

## 2. Resume-Oriented Target Positioning

After the upgrade, the project can be described as:

> **LearningAgent: a personalized AI learning agent with MCP integration, multi-scope long-term memory, hybrid retrieval, agent observability, and adaptive learning feedback.**

Recommended resume bullets after implementation:

- Built an MCP-compatible AI learning agent exposing learning plans, notes, quizzes, and summaries as MCP Tools, Resources, and Prompts.
- Designed a multi-scope long-term memory system separating user, domain, session, and agent-level memories for personalization and context isolation.
- Implemented hybrid memory retrieval combining vector similarity, keyword matching, entity-aware ranking, recency, and importance weighting.
- Built an agent trace and evaluation framework for intent routing, tool calls, memory retrieval, LLM invocations, error recovery, and output quality checks.
- Implemented an adaptive learning loop that tracks concept-level mastery from quiz performance, note coverage, and session history.

---

## 3. Scope and Non-Goals

### In Scope

- Preserve existing CLI commands: `/create`, `/add`, `/vibe`, `/summary`, `/list`, `/exit`.
- Add memory infrastructure behind existing flows.
- Add agent trace collection without changing user-visible behavior.
- Add an MCP server as a separate entry point.
- Add tests for every new module.
- Keep storage local-first and Markdown/JSON based.

### Out of Scope

- Building a full web UI.
- Replacing HelloAgents.
- Replacing all file storage with a database.
- Adding authentication or multi-user server deployment.
- Implementing a full knowledge graph database.
- Training or fine-tuning models.

---

## 4. File Structure Plan

### New Files

- `core/memory_schema.py`
  - Defines `MemoryRecord`, `MemoryScope`, `MemoryType`, and serialization helpers.

- `core/memory_store.py`
  - Stores and reads memory records as JSONL files under `~/.learningAgent/memory/`.

- `core/entity_extractor.py`
  - Extracts lightweight entities from learning text using deterministic rules.

- `core/memory_retriever.py`
  - Implements hybrid retrieval using semantic, keyword, entity, recency, and importance signals.

- `core/tracing.py`
  - Records structured agent execution traces.

- `core/evaluation.py`
  - Scores traces and outputs using deterministic evaluation rules.

- `core/mastery_tracker.py`
  - Maintains concept-level mastery scores for each learning domain.

- `mcp_server/__init__.py`
  - Marks MCP server package.

- `mcp_server/server.py`
  - Starts the LearningAgent MCP server.

- `mcp_server/tools.py`
  - Exposes LearningAgent operations as MCP tools.

- `mcp_server/resources.py`
  - Exposes learning plans, notes, summaries, and sessions as MCP resources.

- `mcp_server/prompts.py`
  - Provides reusable learning workflow prompt templates.

### Modified Files

- `processors/add_knowledge.py`
  - Fix existing `domain` variable bug.
  - Write important note metadata into `MemoryStore`.
  - Use conflict detection before saving notes.

- `agents/vibe_learning_agent.py`
  - Record quiz answers and weak concepts into memory and mastery tracker.
  - Add trace events for question generation and feedback generation.

- `agents/summary_agent.py`
  - Retrieve relevant memories before generating progress reports.
  - Include mastery data in progress analysis.

- `core/main_agent.py`
  - Wrap command processing with trace lifecycle.

- `requirements.txt`
  - Add MCP SDK and BM25 dependency only if implementation uses them directly.

- `README.md`
  - Add new architecture and usage examples after implementation.

### New Tests

- `tests/test_core/test_memory_schema.py`
- `tests/test_core/test_memory_store.py`
- `tests/test_core/test_entity_extractor.py`
- `tests/test_core/test_memory_retriever.py`
- `tests/test_core/test_tracing.py`
- `tests/test_core/test_evaluation.py`
- `tests/test_core/test_mastery_tracker.py`
- `tests/test_processors/test_add_knowledge_memory.py`
- `tests/test_agents/test_summary_memory_integration.py`
- `tests/test_mcp_server/test_tools.py`
- `tests/test_mcp_server/test_resources.py`

---

## 5. Implementation Roadmap

## Phase 0: Stabilize Existing Behavior

**Purpose:** Fix known issues before adding new agent infrastructure.

### Task 0.1: Fix metadata extraction bug in `AddKnowledgeProcessor`

**Files:**

- Modify: `processors/add_knowledge.py`
- Test: `tests/test_processors/test_add_knowledge.py`

- [ ] **Step 1: Add regression test**

Add a test that calls metadata parsing on an LLM-style response and verifies no `NameError` occurs.

Expected behavior:

```python
metadata = processor._extract_metadata_from_text(response, domain="Python")
assert metadata["domain"] == "Python"
assert metadata["category"]
```

- [ ] **Step 2: Run failing test**

Run:

```bash
pytest tests/test_processors/test_add_knowledge.py -v
```

Expected: test fails because `_extract_metadata_from_text` does not accept `domain`.

- [ ] **Step 3: Modify method signature**

Change:

```python
def _extract_metadata_from_text(self, text: str) -> Dict[str, any]:
```

To:

```python
def _extract_metadata_from_text(self, text: str, domain: str) -> Dict[str, any]:
```

Update caller:

```python
return self._extract_metadata_from_text(response, domain)
```

- [ ] **Step 4: Run tests**

Run:

```bash
pytest tests/test_processors/test_add_knowledge.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add processors/add_knowledge.py tests/test_processors/test_add_knowledge.py
git commit -m "fix: preserve domain during knowledge metadata extraction"
```

---

## Phase 1: Multi-Scope Long-Term Memory

**Purpose:** Add a practical memory layer that stores learning facts, preferences, weak concepts, milestones, and session outcomes.

### Task 1.1: Define memory schema

**Files:**

- Create: `core/memory_schema.py`
- Test: `tests/test_core/test_memory_schema.py`

Memory records must support these fields:

```python
id: str
user_id: str
domain: str
session_id: str | None
agent_id: str
memory_type: str
content: str
entities: list[str]
importance: float
confidence: float
source: str
metadata: dict
created_at: str
updated_at: str
access_count: int
```

Supported `memory_type` values:

- `fact`
- `preference`
- `weakness`
- `milestone`
- `misconception`
- `resource`
- `session_summary`

- [ ] **Step 1: Write schema tests**

Test cases:

- Creating a record fills timestamps.
- Importance and confidence are clamped to `[0.0, 1.0]`.
- `to_dict()` and `from_dict()` round-trip without data loss.
- Invalid `memory_type` raises `ValueError`.

- [ ] **Step 2: Implement schema**

Use `dataclasses.dataclass` and standard-library `datetime` only.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_memory_schema.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add core/memory_schema.py tests/test_core/test_memory_schema.py
git commit -m "feat: add multi-scope memory schema"
```

### Task 1.2: Implement local memory store

**Files:**

- Create: `core/memory_store.py`
- Test: `tests/test_core/test_memory_store.py`

Storage layout:

```text
~/.learningAgent/memory/
├── records.jsonl
├── by_domain/
│   └── Python.jsonl
└── indexes/
    └── entities.json
```

Required methods:

```python
add(record: MemoryRecord) -> str
list_by_domain(domain: str, limit: int = 100) -> list[MemoryRecord]
list_by_user(user_id: str, limit: int = 100) -> list[MemoryRecord]
list_by_session(session_id: str, limit: int = 100) -> list[MemoryRecord]
get(memory_id: str) -> MemoryRecord | None
delete(memory_id: str) -> bool
```

- [ ] **Step 1: Write storage tests**

Use `tmp_path` so tests do not write to real home directories.

- [ ] **Step 2: Implement append-only JSONL storage**

Use deterministic JSON serialization with `ensure_ascii=False`.

- [ ] **Step 3: Implement delete using tombstone rewrite**

For MVP, delete can rewrite `records.jsonl` without the target record.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_core/test_memory_store.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add core/memory_store.py tests/test_core/test_memory_store.py
git commit -m "feat: add local long-term memory store"
```

---

## Phase 2: Hybrid Memory Retrieval

**Purpose:** Make memory useful by retrieving learning context with multiple signals instead of pure vector similarity.

### Task 2.1: Add entity extractor

**Files:**

- Create: `core/entity_extractor.py`
- Test: `tests/test_core/test_entity_extractor.py`

MVP entity extraction rules:

- Extract Markdown headings as entities.
- Extract backticked code terms like `useEffect`.
- Extract CamelCase words.
- Extract common technical words from a curated set: `Python`, `React`, `Transformer`, `RAG`, `MCP`, `Agent`, `FAISS`, `BM25`.
- Deduplicate while preserving order.

- [ ] **Step 1: Write tests**

Test input:

```markdown
# React Hooks
`useEffect` handles side effects in React.
LearningAgent uses MCP and BM25 retrieval.
```

Expected entities include:

```python
["React Hooks", "useEffect", "React", "LearningAgent", "MCP", "BM25"]
```

- [ ] **Step 2: Implement extractor**

Use only `re` and standard library.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_entity_extractor.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add core/entity_extractor.py tests/test_core/test_entity_extractor.py
git commit -m "feat: add lightweight entity extractor"
```

### Task 2.2: Implement hybrid retriever

**Files:**

- Create: `core/memory_retriever.py`
- Test: `tests/test_core/test_memory_retriever.py`

Scoring formula:

```text
final_score =
  0.40 * semantic_score
+ 0.25 * keyword_score
+ 0.20 * entity_score
+ 0.10 * importance
+ 0.05 * recency_score
```

MVP implementation rules:

- `semantic_score`: use `sentence-transformers` if available; fall back to TF-IDF cosine similarity.
- `keyword_score`: use TF-IDF overlap from scikit-learn.
- `entity_score`: intersection ratio between query entities and memory entities.
- `importance`: stored memory importance.
- `recency_score`: `1.0` for records from today, gradually lower for older records.

- [ ] **Step 1: Write tests**

Test that a query for `useEffect dependency array` ranks a memory containing `useEffect` and `React` above unrelated Python content.

- [ ] **Step 2: Implement retriever with graceful fallback**

If embedding model loading fails, retrieval must still work using keyword and entity scores.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_memory_retriever.py -v
```

Expected: all tests pass without network access.

- [ ] **Step 4: Commit**

```bash
git add core/memory_retriever.py tests/test_core/test_memory_retriever.py
git commit -m "feat: add hybrid memory retrieval"
```

---

## Phase 3: Agent Trace and Evaluation

**Purpose:** Add production-style observability so the project demonstrates real Agent engineering, not only prompt calls.

### Task 3.1: Add trace recorder

**Files:**

- Create: `core/tracing.py`
- Test: `tests/test_core/test_tracing.py`

Trace schema:

```json
{
  "trace_id": "trace_...",
  "command": "/summary Python",
  "intent": "summary",
  "agent": "SummaryAgent",
  "started_at": "...",
  "ended_at": "...",
  "status": "success",
  "steps": [
    {
      "type": "memory_retrieval",
      "name": "retrieve_summary_context",
      "status": "success",
      "latency_ms": 31,
      "metadata": {"top_k": 5}
    }
  ]
}
```

Required API:

```python
start_trace(command: str, intent: str, agent: str) -> str
add_step(trace_id: str, step_type: str, name: str, status: str, metadata: dict | None = None) -> None
end_trace(trace_id: str, status: str, error: str | None = None) -> None
read_trace(trace_id: str) -> dict | None
```

- [ ] **Step 1: Write tests**

Verify trace lifecycle and JSON persistence under `tmp_path`.

- [ ] **Step 2: Implement trace recorder**

Store traces under:

```text
~/.learningAgent/traces/YYYY-MM-DD/trace_id.json
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_tracing.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add core/tracing.py tests/test_core/test_tracing.py
git commit -m "feat: add agent trace recorder"
```

### Task 3.2: Add deterministic agent evaluator

**Files:**

- Create: `core/evaluation.py`
- Test: `tests/test_core/test_evaluation.py`

Evaluation dimensions:

- `intent_detected`: command has a non-unknown intent.
- `tool_success_rate`: successful steps divided by total steps.
- `memory_used`: trace contains memory retrieval for summary/vibe flows.
- `error_recovered`: failed steps are followed by fallback or graceful final status.
- `output_format_valid`: output contains required sections for plan or summary.

- [ ] **Step 1: Write tests**

Create fake traces and expected evaluation scores.

- [ ] **Step 2: Implement evaluator**

Return:

```python
{
  "score": 0.86,
  "checks": {
    "intent_detected": true,
    "tool_success_rate": 1.0,
    "memory_used": true,
    "error_recovered": true,
    "output_format_valid": true
  }
}
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_evaluation.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add core/evaluation.py tests/test_core/test_evaluation.py
git commit -m "feat: add deterministic agent evaluation"
```

---

## Phase 4: Integrate Memory into Learning Flows

**Purpose:** Connect new infrastructure to existing user-visible features.

### Task 4.1: Add memory writes to knowledge ingestion

**Files:**

- Modify: `processors/add_knowledge.py`
- Test: `tests/test_processors/test_add_knowledge_memory.py`

Behavior:

- After a note is saved, create a `MemoryRecord`.
- Use extracted category, tags, concepts, and summary as metadata.
- Use `memory_type="fact"` for normal notes.
- Use `source="add_knowledge"`.
- Use `importance=0.6` by default.

- [ ] **Step 1: Write test**

Mock `MemoryStore.add()` and assert it receives a record with correct domain and content.

- [ ] **Step 2: Implement integration**

Initialize `MemoryStore` in `AddKnowledgeProcessor.__init__`.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_processors/test_add_knowledge_memory.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add processors/add_knowledge.py tests/test_processors/test_add_knowledge_memory.py
git commit -m "feat: persist knowledge notes into long-term memory"
```

### Task 4.2: Add memory retrieval to progress summary

**Files:**

- Modify: `agents/summary_agent.py`
- Test: `tests/test_agents/test_summary_memory_integration.py`

Behavior:

- Retrieve top 5 relevant memories for the domain.
- Include retrieved memory summaries in the LLM prompt.
- If retrieval fails, continue with existing plan/knowledge/session summaries.

- [ ] **Step 1: Write test**

Mock retriever to return one memory and assert the LLM prompt contains that memory content.

- [ ] **Step 2: Implement integration**

Add retriever initialization and prompt section:

```text
【长期记忆】
- memory content 1
- memory content 2
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_agents/test_summary_memory_integration.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add agents/summary_agent.py tests/test_agents/test_summary_memory_integration.py
git commit -m "feat: use long-term memory in progress summaries"
```

---

## Phase 5: Adaptive Learning Feedback

**Purpose:** Make `/vibe` and `/summary` evidence-driven instead of purely LLM-estimated.

### Task 5.1: Add mastery tracker

**Files:**

- Create: `core/mastery_tracker.py`
- Test: `tests/test_core/test_mastery_tracker.py`

Concept state:

```json
{
  "domain": "Python",
  "concept": "decorator",
  "mastery": 0.62,
  "confidence": 0.74,
  "attempt_count": 5,
  "correct_count": 3,
  "mistake_count": 2,
  "last_practiced_at": "...",
  "review_due_at": "..."
}
```

Update rule:

- Correct answer: `mastery += 0.08`.
- Incorrect answer: `mastery -= 0.10`.
- Clamp mastery to `[0.0, 1.0]`.
- After a mistake, set `review_due_at` to tomorrow.
- After correct answer, set `review_due_at` to three days later.

- [ ] **Step 1: Write tests**

Test correct update, incorrect update, clamping, and due-date behavior.

- [ ] **Step 2: Implement tracker**

Store state under:

```text
~/.learningAgent/<domain>/mastery.json
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_core/test_mastery_tracker.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add core/mastery_tracker.py tests/test_core/test_mastery_tracker.py
git commit -m "feat: track concept-level mastery"
```

### Task 5.2: Connect quiz feedback to mastery tracker

**Files:**

- Modify: `agents/vibe_learning_agent.py`
- Test: `tests/test_agents/test_vibe_learning_agent.py`

Behavior:

- When quiz mode evaluates an answer, extract concept from question metadata or question text.
- Determine correctness from feedback result.
- Update mastery tracker.
- Store weakness memory when answer is incorrect.

- [ ] **Step 1: Add tests**

Mock quiz feedback and assert `MasteryTracker.update()` is called.

- [ ] **Step 2: Implement integration**

Use fallback concept value `general` when concept extraction fails.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_agents/test_vibe_learning_agent.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add agents/vibe_learning_agent.py tests/test_agents/test_vibe_learning_agent.py
git commit -m "feat: update mastery from quiz sessions"
```

---

## Phase 6: MCP-Compatible Server

**Purpose:** Expose LearningAgent as a modern, standards-aligned Agent service.

### Task 6.1: Add MCP tool wrappers

**Files:**

- Create: `mcp_server/__init__.py`
- Create: `mcp_server/tools.py`
- Test: `tests/test_mcp_server/test_tools.py`

Tool functions:

```python
create_learning_plan(input_text: str) -> str
add_knowledge(domain: str, content: str) -> str
get_progress_summary(domain: str) -> str
search_learning_memory(domain: str, query: str, top_k: int = 5) -> list[dict]
```

- [ ] **Step 1: Write tests**

Mock underlying agents/processors and assert wrapper functions return expected strings or dictionaries.

- [ ] **Step 2: Implement wrappers**

Keep wrappers framework-neutral first. Do not require MCP SDK in unit tests.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_mcp_server/test_tools.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add mcp_server/__init__.py mcp_server/tools.py tests/test_mcp_server/test_tools.py
git commit -m "feat: add MCP tool wrappers"
```

### Task 6.2: Add MCP resources and prompts

**Files:**

- Create: `mcp_server/resources.py`
- Create: `mcp_server/prompts.py`
- Test: `tests/test_mcp_server/test_resources.py`

Resources:

```text
learning://domains
learning://domain/{domain}/plan
learning://domain/{domain}/knowledge_summary
learning://domain/{domain}/session_summary
learning://domain/{domain}/mastery
```

Prompts:

- `learn_from_github_repo`
- `paper_to_learning_plan`
- `weekly_learning_review`
- `quiz_weak_points`

- [ ] **Step 1: Write tests**

Verify resource URI parsing and prompt template rendering.

- [ ] **Step 2: Implement resources and prompts**

Use `FileManager` for reads. Return clear error strings when data does not exist.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_mcp_server/test_resources.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add mcp_server/resources.py mcp_server/prompts.py tests/test_mcp_server/test_resources.py
git commit -m "feat: expose learning resources and prompts"
```

### Task 6.3: Add MCP server entry point

**Files:**

- Create: `mcp_server/server.py`
- Modify: `requirements.txt`
- Test: `tests/test_mcp_server/test_tools.py`

Implementation rule:

- If MCP SDK is installed, register tools/resources/prompts with the SDK.
- If MCP SDK is missing, print a clear install message and exit gracefully.

Command:

```bash
python -m mcp_server.server
```

- [ ] **Step 1: Add dependency**

Add an MCP SDK dependency compatible with the selected implementation.

- [ ] **Step 2: Implement server entry point**

Keep business logic in `tools.py`, `resources.py`, and `prompts.py` so server transport can change later.

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_mcp_server -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add mcp_server/server.py requirements.txt tests/test_mcp_server
git commit -m "feat: add MCP server entry point"
```

---

## Phase 7: Documentation and Demo

**Purpose:** Make the project easy to evaluate from README and resume.

### Task 7.1: Update README

**Files:**

- Modify: `README.md`

Add sections:

- Modern Agent Architecture
- MCP Integration
- Long-Term Memory
- Hybrid Retrieval
- Agent Trace and Evaluation
- Adaptive Learning Loop
- Demo Commands

- [ ] **Step 1: Add architecture diagram in text**

```text
CLI / MCP Client
      ↓
MainAgent Router
      ↓
CreatePlan | AddKnowledge | VibeLearning | Summary
      ↓
MemoryStore | HybridRetriever | TraceRecorder | MasteryTracker
      ↓
Local Markdown/JSON Storage
```

- [ ] **Step 2: Add demo commands**

```bash
python main.py
python -m mcp_server.server
pytest tests/ -v
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document modern agent architecture"
```

### Task 7.2: Add final project report

**Files:**

- Create: `docs/AGENT_UPGRADE_REPORT.md`

Report sections:

- What was built
- Architecture overview
- Memory design
- Retrieval design
- Evaluation design
- MCP integration
- Known limitations
- Future work
- Resume bullets

- [ ] **Step 1: Write report**

Keep it factual and aligned with implemented behavior.

- [ ] **Step 2: Commit**

```bash
git add docs/AGENT_UPGRADE_REPORT.md
git commit -m "docs: add agent upgrade report"
```

---

## 6. Testing Strategy

Run focused tests after each task, then run the full suite at phase boundaries.

### Per-task test command

```bash
pytest tests/path/to/test_file.py -v
```

### Phase boundary test command

```bash
pytest tests/ -v
```

### Optional quality checks

```bash
black .
flake8 .
mypy .
```

Do not mark a phase complete until tests pass or failures are documented with root cause and next action.

---

## 7. Risk Management

### Risk: MCP SDK API changes

Mitigation:

- Keep business wrappers framework-neutral.
- Keep SDK-specific code only in `mcp_server/server.py`.
- Unit-test wrappers without MCP SDK.

### Risk: Embedding model download breaks offline tests

Mitigation:

- Use lazy loading.
- Fall back to TF-IDF when embedding model is unavailable.
- Tests must not require network access.

### Risk: Memory system becomes too complex

Mitigation:

- Start with JSONL storage.
- Do not introduce a graph database.
- Use entity-aware ranking instead of full graph traversal.

### Risk: Existing CLI behavior regresses

Mitigation:

- Preserve existing command signatures.
- Add integration tests for `/create`, `/add`, `/vibe`, and `/summary`.
- Make new memory/tracing failures non-blocking.

### Risk: LLM output is nondeterministic

Mitigation:

- Keep tests focused on prompt construction, routing, storage, and fallback behavior.
- Mock LLM calls in unit tests.
- Use deterministic evaluators for trace quality.

---

## 8. Suggested Implementation Order

Recommended order for maximum resume value and lowest risk:

1. Phase 0: Stabilize existing behavior.
2. Phase 3: Agent trace and evaluation.
3. Phase 1: Multi-scope memory.
4. Phase 2: Hybrid retrieval.
5. Phase 4: Memory integration.
6. Phase 6: MCP server.
7. Phase 5: Adaptive learning feedback.
8. Phase 7: Documentation and demo.

Reasoning:

- Trace/evaluation is low-risk and immediately improves engineering credibility.
- Memory and retrieval are the technical core.
- MCP is highly visible but should wrap stable functionality.
- Adaptive learning is product-differentiating but depends on memory and quiz data.

---

## 9. Milestone Definition of Done

### Milestone A: Production-style Agent Engineering

Complete when:

- Trace recorder works.
- Evaluator produces deterministic scores.
- Existing CLI tests still pass.

Resume highlight:

> Built an agent observability and evaluation framework for tracing intent routing, tool calls, LLM calls, memory access, and error recovery.

### Milestone B: Long-Term Memory Agent

Complete when:

- Multi-scope memory records are persisted.
- Notes create memory entries.
- Summary uses retrieved memory.
- Hybrid retrieval tests pass.

Resume highlight:

> Implemented multi-scope long-term memory and hybrid retrieval for personalized learning context.

### Milestone C: MCP-compatible Agent

Complete when:

- Tool wrappers work.
- Resources and prompts work.
- `python -m mcp_server.server` starts or exits with clear dependency guidance.

Resume highlight:

> Exposed LearningAgent as an MCP-compatible server with tools, resources, and prompts for external AI clients.

### Milestone D: Adaptive Learning Agent

Complete when:

- Mastery tracker persists concept states.
- Quiz sessions update mastery.
- Summary includes weak concepts and review suggestions.

Resume highlight:

> Built an adaptive learning feedback loop based on quiz performance, note coverage, and session history.

---

## 10. Final Resume Version

After implementation, use this concise resume entry:

**LearningAgent — Personalized AI Learning Agent with MCP and Long-Term Memory**

- Designed a three-layer AI Agent architecture with coordinator, task-specific learning agents, and specialist agents for GitHub repository analysis, paper analysis, and quiz generation.
- Built an MCP-compatible server exposing learning plans, knowledge notes, quizzes, summaries, and memory search as standardized tools/resources/prompts.
- Implemented multi-scope long-term memory and hybrid retrieval combining semantic similarity, keyword matching, entity-aware ranking, recency, and importance scoring.
- Developed agent tracing and deterministic evaluation for intent routing, tool calls, memory retrieval, LLM calls, failure recovery, and output quality validation.
- Added adaptive learning feedback by tracking concept-level mastery from quiz answers, notes, and session history to recommend personalized review tasks.

---

## 11. Immediate Next Step

Start with Phase 0 and Phase 3.

These two phases are small, low-risk, and immediately improve project quality:

```bash
pytest tests/test_processors/test_add_knowledge.py -v
pytest tests/test_core/test_tracing.py -v
pytest tests/test_core/test_evaluation.py -v
```

After those pass, proceed to memory and retrieval infrastructure.
