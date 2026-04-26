---
name: New Machine Setup
description: Checklist for moving Claude tools, memories, and YouTube MCP to a new machine (Phoenix laptop)
type: reference
---

## Steps

1. **Install Claude Code** — `npm install -g @anthropic-ai/claude-code`

2. **Copy entire `~/.claude/`** — the most important step:
   - `projects/` — all memories
   - `skills/` — all skills (`/tweet`, `/brief`, etc.)
   - `scripts/` — `tweets.py`, `run_tweets.sh`
   - `settings.json` — MCP servers, hooks, config

3. **Copy YouTube MCP** — `~/mcp-servers/youtube/server.js`
   Update path in `~/.claude/settings.json`:
   ```json
   { "mcpServers": { "youtube": { "command": "node", "args": ["/home/<user>/mcp-servers/youtube/server.js"] } } }
   ```

4. **Set up cron** (`crontab -e`):
   ```
   0 8 1,5,10,15,20,25 * * bash ~/.claude/scripts/run_tweets.sh
   ```

5. **Test** — `python3 ~/.claude/scripts/tweets.py`
   Expected: `Accounts: 5/7 OK`, `Tweets: ~10`
