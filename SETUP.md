# Claude Code Setup — New Machine

This repo contains Liran's Claude Code configuration, memories, and YouTube MCP tool.

## What's in here

- `projects/*/memory/` — persistent memories (user profile, BiAgent architecture, Phoenix context)
- `youtube-mcp/` — YouTube transcript MCP server
- `settings.json` — MCP config, model, plugins
- `CLAUDE.md` — global instructions

## Setup Steps

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Clone this repo into ~/.claude
```bash
git clone https://github.com/liran-mazor/claude-config.git ~/.claude
```

### 3. Install YouTube MCP
```bash
mkdir -p ~/mcp-servers/youtube
cp ~/.claude/youtube-mcp/* ~/mcp-servers/youtube/
cd ~/mcp-servers/youtube && npm install
```

### 4. Fix username in settings.json
```bash
sed -i 's|/home/liran|/home/YOUR_USERNAME|g' ~/.claude/settings.json
```
(skip if your username is also `liran`)

### 5. Done
Open Claude Code — memories load automatically. Use the YouTube MCP by pasting any YouTube URL.
