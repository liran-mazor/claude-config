# Claude Code Setup — New Machine

This repo contains Liran's Claude Code configuration, memories, skills, and scripts.
Read this file first, then follow the steps below.

## What's in here

- `projects/` — persistent memory across all conversations (user profile, BiAgent architecture, Phoenix context)
- `skills/` — custom slash commands: `/tweet`
- `scripts/` — `tweets.py` + `run_tweets.sh` (Twitter digest via Nitter)
- `settings.json` — MCP servers, hooks, plugins, model config
- `CLAUDE.md` — global instructions for all projects

## Setup Steps

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Clone this repo into ~/.claude
```bash
# Backup existing config if any
mv ~/.claude ~/.claude.bak 2>/dev/null || true

# Clone
git clone https://github.com/YOUR_USERNAME/claude-config.git ~/.claude
```

### 3. Install YouTube MCP
```bash
mkdir -p ~/mcp-servers
# Copy youtube/server.js from old machine or re-download
# Then update the path in ~/.claude/settings.json:
# "args": ["/home/YOUR_USERNAME/mcp-servers/youtube/server.js"]
```

### 4. Fix paths in settings.json
Two paths need your username updated:
- Hook: `python3 /home/liran/.claude/hooks/phoenix_start.py` → replace `liran` with your username
- MCP: `/home/liran/mcp-servers/youtube/server.js` → replace `liran` with your username

```bash
sed -i 's|/home/liran|/home/YOUR_USERNAME|g' ~/.claude/settings.json
```

### 5. Make scripts executable
```bash
chmod +x ~/.claude/scripts/run_tweets.sh
```

### 6. Set up cron
```bash
crontab -e
# Add this line:
0 8 1,5,10,15,20,25 * * bash ~/.claude/scripts/run_tweets.sh
```

### 7. Test
```bash
python3 ~/.claude/scripts/tweets.py
# Expected: Accounts: 5/7 OK, Tweets: ~10
```

### 8. Run initial tweet fetch
```bash
python3 ~/.claude/scripts/tweets.py
```
Then type `/tweet` in Claude Code to get your first briefing.

## What to do after setup

- Read `projects/` memories — Claude Code will load these automatically
- The `/tweet` skill is ready to use immediately
- YouTube MCP: use it on-demand by pasting any YouTube URL
- Memories are auto-updated as you work — no action needed

## Notes

- Twitter accounts tracked: Sam Altman, Ilya Sutskever, Ethan Mollick, Anthropic, OpenAI, Simon Willison, Jim Fan
- Tweets refresh every 5 days via cron
- YouTube: manual curation — paste interesting videos directly to Claude Code
