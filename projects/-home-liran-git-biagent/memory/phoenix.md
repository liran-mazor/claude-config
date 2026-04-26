---
name: Phoenix Financial — Full Context
description: Stack, workflow, BiAgent mapping, GPU/inference infra, day-1 questions
type: project
---

# Phoenix Financial

$200B+ assets, Israel, publicly traded. Agentic AI Systems Engineer role starting May 3, 2026.
NOT just agents — also infra (ECS, Lambda), data layer (SQL/NoSQL), backend integration.

---

## Stack
- **AI:** Bedrock (Claude), AgentCore, MCP
- **Compute:** ECS (long-running orchestrators), Lambda (stateless tools)
- **Data:** SQL (OLTP, audit), NoSQL (read models, fast lookups)
- **Infra:** API Gateway, WAF, IAM, CloudWatch

---

## BiAgent → AWS Mapping

| BiAgent | Phoenix AWS |
|---------|------------|
| agent.ts (loop) | Bedrock AgentCore |
| router.ts (code-driven) | Bedrock decides internally (model-driven) |
| A2A protocol (custom HTTP) | MCP (industry standard) |
| Kong JWT | API Gateway + Lambda Authorizer |
| LangSmith | CloudWatch + X-Ray |
| pgvector | Bedrock Knowledge Bases or OpenSearch |
| Anthropic SDK direct | Bedrock SDK (stays inside AWS network) |

**Key routing difference:** BiAgent routes via hardcoded TypeScript. Phoenix lets Bedrock decide which tools to call and how many steps — emergent, not explicit.

---

## Happy Flow (Query → Answer)

```
User → WAF → API Gateway → Lambda Authorizer (JWT → allowed tools)
→ Lambda/ECS Validator (PII, prompt injection)
→ Bedrock AgentCore (loop + reasoning)
→ MCP tools (Lambda functions: knowledge, analytics, risk)
→ Data stores (OpenSearch for RAG, RDS/DynamoDB for data)
→ Answer
```

---

## Claude Code vs Copilot (argument for switching)

| | Copilot | Cursor 3.0 | Claude Code | Kiro (AWS) |
|--|---------|--------|-------------|------------|
| Context window | 64K | 200K | 200K — entire codebase in context | 200K |
| Agentic tasks | Limited | Parallel agent swarms, multi-repo, SSH, plan mode | Full ReAct loop, multi-step autonomously | Spec-driven continuous loop |
| Spec layer | None | None | None (CLAUDE.md is primitive spec) | Native — first-class artifact |
| Auto-testing | None | None | None | Auto-generates from spec, provably correct |
| Self-correction | None | Limited | Limited | Continuous (test → fail → fix → verify) |
| MCP integration | No | Yes (limited) | Native — internal tools plug in directly | Native (AWS ecosystem) |
| Project memory | No | .cursorrules (basic) | CLAUDE.md — team conventions enforced, checked into git | Steering files (spec artifacts) |
| Personal memory | No | No | ~/.claude/memory — persistent across sessions | No |
| Global preferences | No | Settings only | ~/.claude/CLAUDE.md — personal rules every session | No |
| TypeScript LSP | Basic | Deep | Deep — full type inference, cross-file awareness | Deep |
| Custom hooks | No | No | Yes — validation, audit logging, automation | No |
| Built-in browser | No | Yes | No | No |
| Model transparency | Yes | No (Composer 2 = Kimi K2, undisclosed) | Yes | Yes (Claude via Bedrock) |
| AWS integration | None | None | None | Native (Kiro = AWS product) |
| Availability | GA | GA | GA | Preview/invite-only |
| Cost | Per seat (~$19/mo) | Per seat (~$20/mo) | Per token — cheaper at moderate usage | TBD |

**Updated note:** Cursor 3.0 closed the agentic gap significantly. Kiro bets spec-driven verification > raw agent power. Claude Code's edge: persistent memory, hooks, deep MCP integration, model transparency.

**Strongest argument for Phoenix (Claude Code):** MCP tools → Claude Code can call internal Phoenix tools natively during development. CLAUDE.md → enforce Lambda patterns, AgentCore conventions, security rules team-wide. New dev joins → clones repo → instantly has full project context.

**Strongest argument for Phoenix (Kiro):** AWS-native (same Bedrock/Claude stack), spec files enforce Lambda/AgentCore patterns automatically, auto-generated tests from spec = provably correct agent behavior. Natural fit if Phoenix is already AWS-first.

**Compliance caveat:** Claude Code queries leave to Anthropic servers — may need IT/compliance approval for financial data. Kiro routes through Bedrock — stays inside AWS network, likely compliant by default. Day-1 question: "What's the policy on AI coding assistants and external API calls from dev machines?"

---

## Context & Prompt Engineering — BiAgent vs AWS

| Technique | BiAgent | AWS |
|-----------|---------|-----|
| System prompt | Code (prompts.ts) | Terraform config (instruction field) |
| Router | Full control | Limited — entry Lambda decides simple vs AgentCore |
| Circuit breaker injection | createUserPrompt() | Entry Lambda prepends to inputText |
| Summarization | Full control (summarizer.ts) | AgentCore black box |
| Prompt caching | Manual cache slots | Automatic (Bedrock manages) |
| Token counting | Manual per conversation | CloudWatch metrics |
| Date/context injection | createUserPrompt() | Entry Lambda prepends to inputText |
| Chunk enrichment | Full control (ingest.ts) | Custom pgvector only (Bedrock KB doesn't support it) |
| Interface adaptation | [VOICE_INTERFACE] prefix | Entry Lambda prepends per source |

**Key insight:** everything you lose control over moves into AgentCore's black box. Everything you keep gets pushed into the entry Lambda — the one layer you own between API Gateway and AgentCore. The entry Lambda is your new context engineering layer (replaces createUserPrompt()).

---

## What Transfers from BiAgent
- Circuit breaker pattern (timeout + error threshold for tool calls)
- Parallel tool execution
- Context summarization (avoid long context)
- Audit logging (every query + decision + tool call)
- Prompt versioning (keep in code, not runtime)
- Cost tracking (tokens + model usage)
- Router pattern (cheap model decides before expensive call)

## What Changes
- A2A → MCP (standardized protocol)
- No auth → AgentCore Gateway (JWT + role → tool whitelist)
- Single process → ECS orchestrator + Lambda tools
- LangSmith → CloudWatch + X-Ray

---

## Bedrock vs Self-Hosted Decision

| Situation | Choice |
|-----------|--------|
| High volume + simple task (routing/classification) | Self-host Llama/Gemma |
| Complex reasoning | Bedrock Claude |
| Long context (100K+) | Bedrock (Claude 200K, no VRAM math) |
| Low volume any complexity | Bedrock (no idle GPU cost) |

Phoenix likely uses Bedrock for main reasoning, self-hosted small model for high-volume routing (Llama 7B/Gemma mentioned in interview).

---

## GPU / Inference Sizing (Mental Model)

**Sizing flow:**
1. Throughput = req/sec × total tokens (input + output)
2. Model quality bar → smallest model that fits
3. GPUs for compute = throughput / model tokens/sec (Llama 3 8B ≈ 3K tok/sec on A100)
4. KV cache check = (VRAM - weights - 3GB overhead) × 0.90 / KV per request
5. Bottleneck = whichever of compute/memory needs more GPUs
6. Cost = GPU fleet/month vs Bedrock per-token at same volume

**KV cache key facts:**
- Grows linearly with context (4x context = 4x cache)
- GQA (Llama 3, Gemma) = 4x less cache than non-GQA (Llama 2)
- vLLM allocates 90% of remaining VRAM to KV pool (PagedAttention)
- 1 model per GPU in production (maximize KV headroom for batching)
- Tensor parallelism when model > single GPU VRAM (vLLM --tensor-parallel-size N)

**Reference (Llama 3 8B INT8, A100 80GB):**
```
Weights: 8GB | Overhead: 3GB | KV pool: 62GB
KV per 1K tokens: 0.125GB (GQA)
Max concurrent at 1K context: ~496 requests
Throughput: ~3,000 tokens/sec with vLLM
```

**vLLM vs Ollama:** vLLM = production (continuous batching, PagedAttention, tensor parallelism). Ollama = local dev only.

---

## Business Side ("Facing the Business")

At Phoenix you work directly with underwriters, claims staff, portfolio managers — not just engineering.
Flow: stakeholder pain point → translate to agent design → build → deliver → monitor.

Key financial terms to know: policy, premium, claim, underwriter, audit trail, compliance.

---

## AI Technical Debt

**Strategic vs reckless:** Strategic = conscious, documented, time-bound, has remediation plan. Reckless = no plan, just a future mess. AI debt compounds faster than traditional software because it's non-deterministic — "change anything, changes everything."

| Category | What gets skipped | Phoenix risk level |
|---|---|---|
| **Prompt debt** | Undocumented system prompts, no injection protection, no guardrails, no input validation | HIGH — financial data + PII leakage = lawsuits |
| **Model debt** | No versioning, no evals, no rollback capability | HIGH — can't pull back broken model in prod |
| **Data debt** | No bias check, no drift detection, no PII anonymization, no poisoning protection | HIGH — $200B AUM, regulated |
| **Org debt** | No governance, no red teaming, no ownership, no scalability plan | HIGH — who gets paged? who signs off? |

**Day 1 posture:** You can name all four categories and their risks. Most juniors can't. Use this to ask smart questions, not to lecture. Find out which debts already exist before suggesting fixes.

---

## MCP — Two Techniques to Check in Phoenix Repo

**1. Progressive discovery** — tools loaded on demand, not all dumped into context window. Critical at Phoenix scale (20+ tools). Check if AgentCore/MCP setup loads tools lazily or dumps everything upfront.

**2. Programmatic tool calling** — instead of model calling tool → result → call another tool → result (sequential, slow, expensive), give model an execution environment to write a script composing tools in one shot. Check if Phoenix uses this pattern or naive sequential calls.

**3. Entry Lambda checklist** — check if entry Lambda handles all of:
- Long query rejection (DoS) — should be API Gateway body size limit first, then Lambda token check. If missing → gap to fill.
- Circuit breaker state injection — reads CloudWatch metrics, prepends degraded tools to inputText
- Date + interface injection — current date, source (web/telegram/copilot)
- Tool selection (router) — cheap model selects subset of tools before AgentCore sees them. Check if AgentCore supports dynamic tool subsets or if full catalog always loaded.
- Invoke AgentCore with enriched query + filtered tools

---

## AWS Infrastructure Knowledge Map

### Covered (understands conceptually)
- **AgentCore** — managed ReAct loop, action groups (Lambda tools), instruction = system prompt in Terraform, limited context control
- **Bedrock** — model platform AgentCore sits on top of, model config not in code
- **Lambda** — stateless tools (action groups), validator, entry Lambda (context enrichment), < 15 min workloads
- **ECS + Fargate** — ECS orchestrates containers, Fargate is serverless compute. Used for MCP server + long-running orchestrators. ECS preferred over EKS for AWS-native shops (simpler, no K8s overhead)
- **API Gateway** — entry point, rate limiting, SSL, routes to Lambda Authorizer
- **WAF** — separate service attached to API Gateway via config, blocks attacks before they hit your code
- **IAM** — AWS service-to-service permissions (Lambda → Bedrock etc). No secrets in code, temporary credentials, least privilege. DevOps owns policies, you open tickets.
- **CloudWatch + X-Ray** — X-Ray = distributed trace across Lambda→AgentCore→Lambda (your main debugger). CloudWatch logs = source for nightly eval queries. Metrics = circuit breaker state input.
- **Cognito** — user auth (human → JWT). Different from IAM (service-to-service). Front door vs internal doors.
- **Okta/Ping Identity** — enterprise SSO. Phoenix likely uses one. Okta for tech companies, Ping for regulated/financial. Issues JWTs for employees. MCP server auth plugs into this.
- **Ragas** — Python eval framework for RAG pipelines. Uses LLM-as-judge internally. Metrics: faithfulness (hallucination), answer relevancy, context recall, context precision. Feed: question + answer (live) + chunks (live) + ground_truth (golden dataset). Run nightly, not every PR (LLM calls = cost).
- **Golden dataset** — static JSON of 20-50 Q&A pairs written by humans (underwriters at Phoenix). Questions stay fixed, answers come from live pipeline at eval time. Stored in S3 or git.
- **vLLM** — production inference server running ON the GPU instance. Continuous batching + PagedAttention. Exposes OpenAI-compatible REST API. vs Ollama = local dev only.
- **Tensor parallelism vs Pipeline parallelism** — how to split model across GPUs when it doesn't fit on one.

### Gaps (not yet covered)
- **Bedrock Guardrails** — config for PII masking, topic blocking, hallucination grounding check. Know it exists, haven't gone deep.
- **Bedrock Knowledge Bases** — managed RAG. Know limitations (no chunk enrichment). Haven't seen config/setup.
- **MCP protocol internals** — know what it does conceptually, haven't seen wire protocol or how to build a server from scratch.
- **Terraform/IaC** — know it's how infra is configured (AgentCore instruction, WAF attachment). Zero hands-on.
- **CDK** — AWS's code-based IaC alternative to Terraform. Not covered.
- **Step Functions** — AWS orchestration for multi-step workflows. Not covered, may be relevant for complex agent flows.
- **SQS/SNS** — AWS messaging (vs Kafka). Not covered.
- **VPC/networking** — subnets, security groups, private endpoints. Not covered.
- **Secrets Manager** — where API keys/secrets live in AWS (vs .env). Not covered.

---

## Multi-Agent Team Roles (check Phoenix architecture against this)

| Role | What it does | BiAgent equivalent |
|---|---|---|
| **Doer** | Executes individual steps | Tool execution |
| **Planner** | Breaks complex task into steps | Router (pattern decision) |
| **Tool Operator** | Calls APIs, runs code | A2A tools (analytics, knowledge) |
| **Learner** | Retrieves info from outside world | RAG pipeline |
| **Critic/Feedback** | Reviews output, checks hallucinations, scores alternatives | None in BiAgent (gap) |
| **Supervisor** | Monitors progress, unsticks failures | Circuit breaker |
| **Presenter** | Synthesizes and communicates back | Final answer synthesis |

ReAct = Planner + Tool Operator + Critic + Presenter (what BiAgent's agent.ts implements).

**Key gap to check at Phoenix:** Does their architecture have a critic/feedback role? Most teams skip it. Cross-provider review (one model writes, another challenges) is the most promising pattern — directly applicable to agent tool output verification. If missing, this is a gap to fill.

---

## Claude Code Hooks & Skills — Things to Explore at Phoenix

- `/standup` skill — pull recent git commits + open tasks, draft a daily standup summary
- `/review-pr` skill — team's specific review checklist (security, cost, naming conventions)
- Hook that auto-runs after sessions to log what was changed (audit trail for work at Phoenix)

---

## Day 1 Questions to Ask
*(code answers: agent protocol, tool definitions, observability stack, ECS vs EKS — read infra/Terraform first)*

1. What does AgentCore actually manage here vs custom code?
2. What's the governance model — who approves new tools before they go to production?
3. What is a "simple" vs "complex" task in their domain?
4. What's our IdP for internal employees, and separate one for customer-facing apps?
5. Who handles IAM policy changes — ticket or self-serve?
6. What's the policy on AI coding assistants and external API calls from dev machines?
7. What evals exist today, if any?
8. Who gets paged when an agent fails in production?
9. What does "done" look like — who signs off before an agent reaches stakeholders?
10. Is there a self-hosted model running alongside Bedrock (router/classifier)?
11. What financial domain should I learn first — claims, policy, or portfolio?
