---
name: BiAgent Architecture Reference
description: BiAgent architecture snapshot for future comparison against Phoenix stack — query lifecycle, tools, RAG, infra
type: project
---

# BiAgent Architecture

Built from scratch, no LangChain/LangGraph. ReAct-pattern autonomous agent.

---

## Query Lifecycle

```
User query
  → routeQuery() — Haiku decides pattern or returns unavailable
  → if unavailable → return immediately, zero LLM calls
  → summarizeIfNeeded() — compress history if >170k tokens
  → markHistoryCacheBoundary() — prompt cache slot 3
  → createUserPrompt() — inject date + circuit breaker warnings

  FUNCTION_CALL path:
    → one tool call + one final answer (Haiku), flat context, no loop

  REACT path:
    → iterative loop: callLLM() (Sonnet) → parallel executeTool() → repeat until final answer
```

---

## Two-Tier Model Strategy

| Task | Model | Reason |
|------|-------|--------|
| Routing, summarization | Haiku | Cheap, fast, classification only |
| ReAct loop, reasoning | Sonnet | Complex multi-step reasoning |

---

## Two-Tier Tool Resolution

| Type | Protocol | Circuit Breaker |
|------|----------|----------------|
| Native | In-process (chart, email, web_search, forecast_revenue) | None — fail fast |
| A2A | HTTP direct to analytics (3002) or knowledge-agent (3001) | Yes — 30s timeout, 50% threshold, 10s reset |

---

## RAG Pipeline (knowledge-agent)

**Index time (ingest.ts):**
```
doc → LLM metadata extraction (doc_type, year, title)
    → chunk (recursive split + overlap)
    → LLM chunk enrichment per chunk:
        - chunk_summary (1 sentence)
        - hypothetical_questions (3 questions this chunk could answer)
        - structure_type (PARAGRAPH, TABLE, CODE_BLOCK, HEADING)
    → embed: chunk content + hypothetical questions concatenated
      (closes semantic gap between user query phrasing and chunk content)
    → upsert into pgvector
```

**Query time (retriever.ts):**
```
Query → embed (same model as index time, must match)
      → pgvector cosine search (TOP_K=20)
      → filter by similarity threshold (0.75)
      → if ≥6 candidates: Cohere rerank → top 5
      → if <6 candidates: skip reranker, take top 5 directly
      → sort chunks by chunk_index (document order, not relevance)
      → gpt-4o-mini synthesis
```

---

## Infrastructure

- **Local/demo:** Docker Compose — pgvector + ClickHouse (no Kafka)
- **Full dev:** Docker Compose + Kafka
- **Production:** K8s — Kong ingress (JWT + rate limiting), ECS-style service topology

---

## Context Management

- Token count tracked per conversation
- Summarization triggers at 170k tokens (85% of 200k limit)
- Haiku compresses via forced tool use → `StructuredSummary` (topic, key_facts, resolved_entities, queries_run, open_questions)
- **Selective injection:** `formatSummaryForContext(summary, query)` — only injects fields relevant to the current query, not the full summary. Avoids bloating context with irrelevant history.
- Prompt cache slot 3 marked after summary injection (`markHistoryCacheBoundary()`)

---

## Circuit Breaker

- opossum-based, keyed by tool name
- A2A only (native tools are in-process)
- Closed-loop: `openCircuits` set updated on every open/close event
- `getOpenCircuits()` called once per `run()`, injected into:
  1. **Router prompt** — Haiku returns `available: false` if required tools are open → zero further LLM calls
  2. **ReAct user prompt** — Sonnet warned about open circuits so it doesn't attempt unavailable tools mid-loop

---

## Key Interfaces

| Interface | What |
|-----------|------|
| CLI single query | `biagent/interfaces/index.ts` |
| Interactive CLI | `biagent/interfaces/interactive.ts` |
| Telegram bot | `biagent/interfaces/telegramBot.ts` |
| Alfred (RPi voice) | `biagent/interfaces/alfred.ts` |

---

## What BiAgent Does NOT Have (vs Production)

- No semantic cache
- No structured logging / observability
- No evals / testing framework
- No persona memory
- No fine-tuning or self-hosted models
- No multi-agent coordination beyond A2A
