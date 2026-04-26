---
name: tweet
description: Read and analyze the latest Twitter digest, filtered for the user's role in agentic AI.
---

Read the file `~/.claude/tweets.md` in full.

Also check `~/.claude/tweets.log` for any `WARN:` lines. If accounts failed or returned 0 tweets, mention it briefly at the top.

Then produce a structured briefing:

1. **Signal** — tweets with direct relevance to agentic AI, LLM inference, agent architecture, Bedrock, MCP, vLLM, or the broader AI engineering stack. One sentence per tweet on what it means and whether to act on it.

2. **Industry Moves** — model releases, company announcements, competitive signals (OpenAI, Anthropic, Google). Context only — no action needed.

3. **Worth Knowing** — opinions, threads, or ideas that are good mental models even if not immediately actionable.

4. **Skip** — briefly list tweets you filtered out and why.

Be concise. Lead with the most actionable items. No filler.
