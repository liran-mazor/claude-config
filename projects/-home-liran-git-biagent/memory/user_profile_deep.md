---
name: Deep User Profile — Knowledge, Gaps, Strengths, Learning Style
description: Comprehensive profile of what Liran knows deeply, where gaps exist, how he learns, and how to calibrate explanations
type: user
---

# Who Liran Is

First job starting May 3, 2026 at Phoenix Financial as Agentic AI Systems Engineer.
Built BiAgent as a self-directed learning project — not a tutorial follower, a builder.
Has deeper foundations than most juniors because he learned by doing, not watching.

---

# Strengths (Deep Knowledge)

## Agent Architecture
- Understands ReAct loop at implementation level — built it from scratch in agent.ts
- Knows two-tier routing: cheap model (Haiku) for routing, expensive model (Sonnet) for reasoning
- Understands FUNCTION_CALL vs REACT patterns and when each applies
- Knows prompt caching (3 cache slots), token counting, context summarization
- Built circuit breaker pattern (opossum) for A2A tools
- Understands degraded mode / fallback model strategy
- Knows forced tool use pattern (router uses it for structured output)

## RAG Pipeline
- Built full pipeline end-to-end: chunking → embedding → pgvector → Cohere rerank → synthesis
- Knows TOP_K over-fetch then filter pattern (retrieve 20, threshold filter, rerank to 5)
- Understands why chunks are sorted back to document order before synthesis (not relevance order)
- Knows embedding model must match at index and query time
- Knows when to skip reranker (< 6 candidates → no value)
- Understands lazy instantiation pattern (getOpenAI(), getPool())

## Event-Driven Architecture
- Built Kafka consumers + ClickHouse analytics pipeline
- Knows outbox pattern (single transaction: entity + outbox row)
- Knows BatchBuffer pattern (flush on count OR timer)
- Understands consumer group isolation

## Backend / TypeScript
- Strong TypeScript: discriminated unions, generics, type guards
- Knows dotenv patterns, module loading order
- Built A2A HTTP protocol with JWT signing
- Knows K8s basics (wrote manifests, Kong ingress, JWT plugin)

## Thinking Style (Strengths)
- Asks WHY before HOW — instinctively challenges architectural decisions
- Cost-conscious — naturally thinks about ROI, per-token vs per-hour math
- Works backwards from business requirements to technical decisions
- Catches inconsistencies (caught the 70B/A100 fit problem immediately)
- Good at spotting when something doesn't add up (the 400 concurrent vs 17 GPU question)

---

# Gaps (Needs Development)

## AWS Services
- Just learned basics in this session: API Gateway, WAF, Lambda, ECS, GPU instances
- Does not yet know: S3, SQS/SNS, CloudWatch, IAM in depth, VPC/networking
- Has no hands-on AWS experience yet

## LLM Inference Infrastructure
**Transformer internals (solid):**
- Tokenization → embedding (per token, dumb lookup) → positional encoding (RoPE) → layers
- Each layer: self-attention (Q/K/V/O) + feedforward (2 matrices)
- Q/K/V/O matrix roles understood: Q=what am I looking for, K=what do I contain, V=what I send
- GQA: K,V heads shared across query groups → computed once per token, stored per layer in KV cache
- KV cache is per-layer, not global — 32-layer model = 32 caches
- Prefill = parallel processing of full context window (compute-bound); decode = sequential token generation (memory-bound)
- Understands why prefill must complete before decode begins
- KV cache sizing math: `2 × layers × KV_heads × d_head × seq_len × bytes`
- Understands why caching full conversation history at Anthropic scale is economically impossible (~$1B/year for 1M users)

**Inference serving (solid):**
- Knows inference server = the layer between model weights and HTTP API (replaces cloud API in self-hosted)
- Ollama vs vLLM across 4 dimensions: batching, KV allocation, multi-GPU, speculative decoding
- PagedAttention: OS virtual memory analogy, fixed-size blocks, block table, solves fragmentation
- Continuous batching vs static batching: slot freed → new request inserted immediately
- Inference server spectrum: Ollama → TGI → vLLM → TensorRT-LLM
- AWS deployment: ECS + EC2 GPU (not Fargate — no GPU support)
- Knows how to swap Anthropic client for vLLM in BiAgent router (OpenAI-compatible API)
- Two-tier cost strategy: self-hosted 8B for routing, cloud Sonnet for reasoning

**Speculative decoding (solid):**
- Draft model (small/fast) guesses N tokens ahead → main model verifies all N in one parallel pass
- Speedup = parallelism, not matrix reuse
- Production standard in vLLM, TGI, TensorRT-LLM. ~2-3x latency at low concurrency
- Degrades at high concurrency — continuous batching already keeps GPU busy
- Configured at inference server level, requires two models from same family
- Closed APIs (Claude, GPT-4) don't disclose but almost certainly use similar internally

**Ollama vs vLLM (solid):**
| | Ollama | vLLM |
|---|---|---|
| Continuous batching | ❌ | ✓ |
| PagedAttention | ❌ | ✓ |
| Tensor parallelism | ❌ | ✓ |
| Speculative decoding | ❌ | ✓ |
| Multi-GPU | layer split only (slow) | tensor parallel (fast, needs NVLink) |
| Cold start | unloads model when idle | always loaded |
- Ollama = single-user local dev only. Anything production → vLLM

**Gaps remaining:**
- No hands-on experience with vLLM or GPU instances
- Quantization (INT4/INT8) — next relevant topic
- **Skip:** attention math (softmax, √d_k), backprop, training dynamics — out of scope for deployment role

## Bedrock / AgentCore / MCP
- Knows conceptually what they are (from this session)
- Has not used any of them in code
- AgentCore internals not yet covered
- MCP protocol not yet covered in depth

## Financial Domain
- No background in insurance, investment, claims, underwriting
- Does not know: policy, premium, underwriter, claim lifecycle, regulatory requirements
- This is a real gap for Phoenix — needs to learn domain terminology fast

## Production Operations
- No experience with monitoring, alerting, incident response
- Does not know CloudWatch, distributed tracing, observability patterns
- No experience with evals/testing frameworks for agents

## Security
- Knows concepts (WAF, prompt injection, PII) at conceptual level
- No hands-on implementation experience

---

# Learning Style

- **Wants depth** — explicitly said "don't go easy on me because I'm a junior"
- **Learns by calculation** — doing the KV cache math himself solidified it
- **Needs WHY** — explaining the rule without the reason doesn't stick
- **Connects new to known** — explaining AWS via BiAgent analogy works well
- **Challenges assumptions** — pushes back when something doesn't make sense, good sign
- **Prefers short answers** unless asking for deep dive
- **Iterative** — goes one step at a time, confirms understanding before moving on
- **Catches errors** — noticed the 70B/A100 mismatch, noticed the 400 concurrent vs throughput contradiction

---

# How to Calibrate Explanations

- Always anchor new AWS/cloud concepts to BiAgent equivalents first
- Show the math — he learns from calculations, not just rules
- Give the "why this component exists separately" — he will ask
- Don't oversimplify — he pushes back when you do
- When explaining decisions, frame as: business requirement → constraint → architectural choice
- Financial domain: explain terminology when it comes up, don't assume he knows it
- Cost math: he engages with this, include it when relevant
- For GPU/infra: he can handle the formulas, show the full calculation

---

# What Will Make Him Successful at Phoenix

Strengths to leverage:
- Agent pattern knowledge (already ahead of most juniors)
- RAG pipeline understanding (built it end-to-end)
- Architectural thinking (asks good questions)
- Cost awareness (will be valuable in infra discussions)

Areas to develop before May 3:
- AgentCore + MCP (next topics to cover)
- Bedrock Guardrails + Knowledge Bases
- Basic financial domain terminology
- One hands-on AWS exercise if possible

Day 1 posture:
- Lead with agent knowledge (his real edge)
- Ask about existing architecture before suggesting anything
- Learn the financial domain fast — talk to business stakeholders
- Don't pretend to know AWS ops depth — ask, learn, apply
