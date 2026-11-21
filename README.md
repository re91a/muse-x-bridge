# muse-x-bridge

Cross-platform X (Twitter) session-cookie connector skill for AI agents (such as Muse) and automation workflows — works without paid developer API tiers or headless browser pairing.

Designed to run across **Windows, macOS, Linux, Android (Termux), iOS/iPadOS, and Web clients** via dual **CLI** (`x_bridge.py`) and **Bearer-authenticated HTTP Bridge** (`server.py`) modes.

---

## Features

- **Cookie-Session Auth (`twikit==2.3.3`)** — Uses `auth_token` + `ct0` directly instead of fragile browser login flows.
- **Dual Mode Architecture**
  - **Local CLI (`x_bridge.py`)**: For desktop terminals, Termux, or AI agent sandboxes (`whoami`, `post`, `reply`, `quote`, `like`).
  - **HTTP Bridge (`server.py`)**: Lightweight Python HTTP server with Bearer token auth for mobile, iPadOS, and remote browser agents.
- **Built-in Safety Guards**
  - `--dry-run` preview mode before publishing anything.
  - Automatic 10-second cooldown between write actions.
  - Strict `.gitignore` rules to prevent accidental commits of `.env` or `cookies.json`.

---

## Security & Transparency

Before installing or connecting this skill to an AI agent, please note:

1. **Standard AI Agent Confirmation Is Normal**: Because this is an external GitHub repository containing executable Python scripts, AI agents (like Muse) may display a one-time execution confirmation before cloning and installing `twikit==2.3.3`. Always inspect `x_bridge.py` and `server.py` yourself first — the codebase is intentionally short, readable, and contains no hidden hooks or binaries.
2. **Use an Experimental / Secondary Account**: An X `auth_token` grants full session access. For testing and automation experiments, always prefer a dedicated secondary/bot account rather than your primary personal account.
3. **Never Commit Secrets**: Keep `cookies.json` and `.env` local (or inside your agent's secret manager / environment variables). Never paste session cookies into public chats or repositories.

---

## Quick Start

### 1. Install Dependency
```bash
pip install -r requirements.txt
```

### 2. Configure Session Credentials
Copy `.env.example` to `.env` (or `cookies.example.json` to `cookies.json`) and fill in your `auth_token` and `ct0`:

```bash
export X_AUTH_TOKEN="your_auth_token"
export X_CT0="your_ct0"
```

### 3. Verify & Test (CLI Mode)
```bash
python x_bridge.py whoami
python x_bridge.py post --text "Hello from muse-x-bridge" --dry-run
```

### 4. Optional HTTP Bridge Mode (Mobile / Remote Agents)
```bash
export BRIDGE_API_KEY="replace_with_strong_random_secret"
python server.py
```

---

## Repository Structure

| File | Purpose |
| :--- | :--- |
| `SKILL.md` | Agent skill instructions and command reference |
| `x_bridge.py` | Core CLI tool (`whoami`, `post`, `reply`, `quote`, `like`) |
| `server.py` | Bearer-authenticated HTTP bridge for remote/mobile use |
| `requirements.txt` | Pinned dependency (`twikit==2.3.3`) |
| `.env.example` | Environment variable template |
| `cookies.example.json` | Cookie file template |
| `.gitignore` | Blocks `.env`, `cookies.json`, and local caches |

---

## License

MIT License — Built by [@re91a](https://github.com/re91a)
