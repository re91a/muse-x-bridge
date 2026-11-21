# muse-x-bridge

> Cross-platform session-cookie connector & AI Agent Skill (**Muse**) for **X (Twitter)** — works across **Desktop (Windows/macOS/Linux)**, **Android**, **iOS/iPadOS**, **Muse App**, and **Web Browsers**.

## How Cross-Platform Support Works
```text
[Muse Desktop / Termux] ──(CLI)──> x_bridge.py ──┐
                                                 ├──> X Session (Twikit)
[Muse iOS / Android / Web] ─(HTTPS)─> server.py ─┘
```
- **Local Mode (`x_bridge.py`)**: Direct CLI execution on PC, Mac, Linux, VPS, or Android Termux.
- **Bridge Server Mode (`server.py`)**: Lightweight Bearer-authenticated HTTP server so mobile & browser-based Muse clients can connect from anywhere without running Python on the phone.

## Getting `auth_token` & `ct0` on Any Device (One-Time Setup)
Once stored in your server/Muse environment variables (`X_AUTH_TOKEN`, `X_CT0`), you can use Muse from **any device** (including iPhone/iPad) without repeating this step:

- **Laptop / PC (Chrome, Edge, Brave, Firefox):**
  Log in to `x.com` -> Press `F12` -> **Application** (or **Storage**) -> **Cookies** -> Copy `auth_token` and `ct0`.
- **Android Phone (No PC Needed):**
  Use **Kiwi Browser** or **Mises Browser** (supports Chrome DevTools/extensions) to inspect `x.com` cookies, then copy `auth_token` and `ct0`.
- **iOS / iPadOS:**
  Because X sets `auth_token` as `HttpOnly`, standard Safari blocks JavaScript from reading it. Extract once via a PC/Android device or a browser supporting Web Inspector cookie inspection, then save to your remote Bridge env vars.

## Quick Start
### 1. Local CLI
```bash
pip install -r requirements.txt
cp cookies.example.json cookies.json
python x_bridge.py whoami
```

Or import directly from a raw `Cookie` header:
```bash
python x_bridge.py import-header --header "auth_token=xxx; ct0=yyy"
```

### 2. Remote HTTP Bridge (for iOS / Android / Browser Muse)
```bash
export X_AUTH_TOKEN="your_auth_token"
export X_CT0="your_ct0"
export BRIDGE_API_KEY="your_strong_secret"
python server.py
```

## Security Notice
- `auth_token` gives full session access to an X account. **Never commit `.env` or `cookies.json`.**
- Always protect `server.py` behind HTTPS and a strong `BRIDGE_API_KEY`.
- Built for personal experimentation with rate-limit cooldowns and `--dry-run` previews.
