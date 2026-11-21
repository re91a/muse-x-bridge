import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from twikit import Client

DEFAULT_COOKIE_PATH = Path("cookies.json")
STATE_PATH = Path(".last_action_ts")
MIN_WRITE_COOLDOWN_SEC = 10


def parse_cookie_header(raw_header: str) -> Dict[str, str]:
    """Extract auth_token and ct0 from a raw browser Cookie header string."""
    parsed: Dict[str, str] = {}
    for part in raw_header.split(";"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        key = k.strip()
        if key in ("auth_token", "ct0"):
            parsed[key] = v.strip().strip('"')
    return parsed


def load_session_cookies(cookie_file: Path = DEFAULT_COOKIE_PATH) -> Dict[str, str]:
    env_auth = os.getenv("X_AUTH_TOKEN", "").strip()
    env_ct0 = os.getenv("X_CT0", "").strip()

    if env_auth and env_ct0:
        return {"auth_token": env_auth, "ct0": env_ct0}

    raw_header = os.getenv("X_COOKIE_HEADER", "").strip()
    if raw_header:
        header_cookies = parse_cookie_header(raw_header)
        if header_cookies.get("auth_token") and header_cookies.get("ct0"):
            return header_cookies

    if not cookie_file.exists():
        raise FileNotFoundError(
            f"Cookie file '{cookie_file}' not found. Set X_AUTH_TOKEN & X_CT0 env vars, "
            f"or run 'python x_bridge.py import-header --header \"...\"'."
        )

    data = json.loads(cookie_file.read_text(encoding="utf-8"))
    auth_token = str(data.get("auth_token", "")).strip()
    ct0 = str(data.get("ct0", "")).strip()

    if not auth_token or not ct0 or "PASTE_YOUR" in auth_token:
        raise ValueError("Invalid auth_token or ct0 inside cookies.json.")

    return {"auth_token": auth_token, "ct0": ct0}


def enforce_cooldown(dry_run: bool) -> None:
    if dry_run or not STATE_PATH.exists():
        return
    try:
        last_ts = float(STATE_PATH.read_text(encoding="utf-8").strip())
        elapsed = time.time() - last_ts
        if elapsed < MIN_WRITE_COOLDOWN_SEC:
            wait_sec = round(MIN_WRITE_COOLDOWN_SEC - elapsed, 1)
            raise RuntimeError(
                f"Cooldown active to protect account. Wait {wait_sec}s before next write action."
            )
    except ValueError:
        pass


def record_write_timestamp() -> None:
    STATE_PATH.write_text(str(time.time()), encoding="utf-8")


async def execute_action(
    command: str,
    payload: Optional[Dict[str, Any]] = None,
    cookie_file: Path = DEFAULT_COOKIE_PATH,
    dry_run: bool = False,
) -> Dict[str, Any]:
    payload = payload or {}

    if dry_run and command != "whoami":
        return {"dry_run": True, "command": command, "payload": payload}

    cookies = load_session_cookies(cookie_file)
    client = Client("en-US")
    client.set_cookies(cookies)

    if command == "whoami":
        user_id = await client.user_id()
        return {"status": "authenticated", "user_id": user_id}

    enforce_cooldown(dry_run)

    if command == "post":
        text = str(payload.get("text", "")).strip()
        if not text:
            raise ValueError("'text' is required for post.")
        tweet = await client.create_tweet(text=text)
        record_write_timestamp()
        return {"status": "posted", "tweet_id": tweet.id}

    if command == "reply":
        tweet_id = str(payload.get("tweet_id", "")).strip()
        text = str(payload.get("text", "")).strip()
        if not tweet_id or not text:
            raise ValueError("'tweet_id' and 'text' are required for reply.")
        tweet = await client.create_tweet(text=text, reply_to=tweet_id)
        record_write_timestamp()
        return {"status": "replied", "tweet_id": tweet.id, "reply_to": tweet_id}

    if command == "quote":
        url = str(payload.get("url", "")).strip()
        text = str(payload.get("text", "")).strip()
        if not url or not text:
            raise ValueError("'url' and 'text' are required for quote.")
        tweet = await client.create_tweet(text=text, attachment_url=url)
        record_write_timestamp()
        return {"status": "quoted", "tweet_id": tweet.id, "quoted_url": url}

    if command == "like":
        tweet_id = str(payload.get("tweet_id", "")).strip()
        if not tweet_id:
            raise ValueError("'tweet_id' is required for like.")
        await client.favorite_tweet(tweet_id)
        record_write_timestamp()
        return {"status": "liked", "tweet_id": tweet_id}

    raise ValueError(f"Unsupported command: {command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Muse X Bridge — Cross-Platform X Connector")
    parser.add_argument("--cookies", default=str(DEFAULT_COOKIE_PATH), help="Path to cookies JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Preview payload without sending to X")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("whoami", help="Verify cookie session and print user ID")

    p_import = sub.add_parser("import-header", help="Save cookies.json from a raw Cookie header string")
    p_import.add_argument("--header", required=True, help="Raw cookie string containing auth_token and ct0")

    p_post = sub.add_parser("post", help="Create a new post")
    p_post.add_argument("--text", required=True, help="Post content")

    p_reply = sub.add_parser("reply", help="Reply to an existing post ID")
    p_reply.add_argument("--tweet-id", required=True, help="Target tweet ID")
    p_reply.add_argument("--text", required=True, help="Reply content")

    p_quote = sub.add_parser("quote", help="Quote-post an existing X post URL")
    p_quote.add_argument("--url", required=True, help="Full X post URL")
    p_quote.add_argument("--text", required=True, help="Quote commentary")

    p_like = sub.add_parser("like", help="Like a post by ID")
    p_like.add_argument("--tweet-id", required=True, help="Target tweet ID")

    return parser


if __name__ == "__main__":
    try:
        args = build_parser().parse_args()
        cookie_path = Path(args.cookies)

        if args.command == "import-header":
            extracted = parse_cookie_header(args.header)
            if not extracted.get("auth_token") or not extracted.get("ct0"):
                raise ValueError("Could not find both 'auth_token' and 'ct0' in the provided header.")
            cookie_path.write_text(json.dumps(extracted, indent=2), encoding="utf-8")
            print(json.dumps({"status": "saved", "cookies_file": str(cookie_path)}, indent=2))
            sys.exit(0)

        payload_map = {
            "text": getattr(args, "text", None),
            "tweet_id": getattr(args, "tweet_id", None),
            "url": getattr(args, "url", None),
        }
        result = asyncio.run(
            execute_action(args.command, payload_map, cookie_file=cookie_path, dry_run=args.dry_run)
        )
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2), file=sys.stderr)
        sys.exit(1)
