---
name: muse-x-bridge
description: Cross-platform X (Twitter) connector skill for Muse using Twikit session cookies. Works locally via CLI (PC/Linux/Android Termux) or remotely via HTTP Bridge (iOS, iPadOS, Android app, and browser clients).
---

# Muse X Bridge Skill

Choose the execution mode matching where Muse is running:

## Mode A: Local / Sandbox CLI
Requires `X_AUTH_TOKEN` and `X_CT0` env vars (or local `cookies.json`).
- `python x_bridge.py whoami`
- `python x_bridge.py post --text "..." --dry-run`
- `python x_bridge.py post --text "..."`
- `python x_bridge.py reply --tweet-id 1234567890 --text "..."`
- `python x_bridge.py quote --url "https://x.com/user/status/1234567890" --text "..."`
- `python x_bridge.py like --tweet-id 1234567890`

## Mode B: Remote HTTP Bridge (Mobile Apps, iOS, iPadOS, Browser)
When Muse runs in a mobile/browser client without local Python execution, call the deployed `server.py` endpoints with header `Authorization: Bearer <BRIDGE_API_KEY>`:
- `GET /health`
- `POST /whoami`
- `POST /post` (`{"text": "...", "dry_run": false}`)
- `POST /reply` (`{"tweet_id": "...", "text": "..."}`)
- `POST /quote` (`{"url": "...", "text": "..."}`)
- `POST /like` (`{"tweet_id": "..."}`)

## Safety Guardrails
1. Confirm or run `dry_run: true` before publishing public posts.
2. Never print, log, or commit `auth_token`, `ct0`, or `BRIDGE_API_KEY`.
3. Respect the built-in cooldown between write actions.
