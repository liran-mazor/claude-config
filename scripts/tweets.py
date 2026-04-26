#!/usr/bin/env python3
"""
Twitter digest: fetches tweets via Nitter RSS, writes ~/.claude/tweets.md
Triggered by: crontab via run_tweets.sh every 5 days at 8am (days 1,5,10,15,20,25)
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request

HOME = os.path.expanduser("~")
OUTPUT = f"{HOME}/.claude/tweets.md"
CUTOFF = datetime.now(timezone.utc) - timedelta(days=5)

NITTER_INSTANCE = "https://nitter.net"
TWITTER_ACCOUNTS = {
    "sama":        "Sam Altman",
    "ilyasut":     "Ilya Sutskever",
    "emollick":    "Ethan Mollick",
    "AnthropicAI": "Anthropic",
    "OpenAI":      "OpenAI",
    "simonw":      "Simon Willison",
    "drjimfan":    "Jim Fan",
}


def fetch(url, timeout=10):
    try:
        req = Request(url, headers={"User-Agent": "tweets-bot/1.0"})
        with urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  WARN: {url}: {e}", file=sys.stderr)
        return None


def parse_date(s):
    if not s:
        return None
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
                "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"]:
        try:
            dt = datetime.strptime(s.strip(), fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except:
            pass
    return None


def fetch_tweets(username, display_name):
    data = fetch(f"{NITTER_INSTANCE}/{username}/rss")
    if not data:
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    items = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el  = item.find("link")
        date_el  = item.find("pubDate")

        title = title_el.text if title_el is not None else ""
        link  = link_el.text  if link_el  is not None else ""
        date  = parse_date(date_el.text if date_el is not None else "")

        if date and date < CUTOFF:
            continue
        if not title:
            continue

        items.append({"author": display_name, "title": title, "url": link})
        if len(items) >= 2:
            break

    return items


def main():
    print("Fetching tweets...", file=sys.stderr)

    all_items = []
    ok, failed = 0, []

    for username, display_name in TWITTER_ACCOUNTS.items():
        tweets = fetch_tweets(username, display_name)
        print(f"  {display_name}: {len(tweets)}", file=sys.stderr)
        if tweets:
            ok += 1
        else:
            failed.append(display_name)
        all_items.extend(tweets)

    total = ok + len(failed)
    summary = f"Accounts: {ok}/{total} OK"
    if failed:
        summary += f" — failed/empty: {', '.join(failed)}"
    print(f"  {summary}", file=sys.stderr)
    print(f"  Tweets: {len(all_items)}", file=sys.stderr)

    now = datetime.now().strftime("%Y-%m-%d")
    raw = "\n".join(f"- [{i['author']}] {i['title']} — {i['url']}" for i in all_items)

    content = f"""---
updated: {now}
accounts: {ok}/{total}
failed: {', '.join(failed) if failed else 'none'}
tweets: {len(all_items)}
---

# Twitter Digest — {now}

{raw}
"""

    with open(OUTPUT, "w") as f:
        f.write(content)

    print(f"Done → {OUTPUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
