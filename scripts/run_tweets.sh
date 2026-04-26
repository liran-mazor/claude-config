#!/bin/bash
# Wrapper for tweets.py — loads shell env for cron
source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null || true
python3 "$(dirname "$0")/tweets.py" >> ~/.claude/tweets.log 2>&1
