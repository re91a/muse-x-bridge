import asyncio
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

from x_bridge import execute_action

API_KEY = os.getenv("BRIDGE_API_KEY", "").strip()
PORT = int(os.getenv("PORT", "8787"))
HOST = os.getenv("HOST", "0.0.0.0")


class BridgeHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, body: Dict[str, Any]) -> None:
        raw = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _is_authorized(self) -> bool:
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:].strip()
        return bool(API_KEY) and hmac.compare_digest(token, API_KEY)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "muse-x-bridge"})
            return
        self._send_json(404, {"status": "error", "message": "Not found"})

    def do_POST(self) -> None:
        if not self._is_authorized():
            self._send_json(401, {"status": "error", "message": "Unauthorized"})
            return

        command_map = {
            "/whoami": "whoami",
            "/post": "post",
            "/reply": "reply",
            "/quote": "quote",
            "/like": "like",
        }
        command = command_map.get(self.path)
        if not command:
            self._send_json(404, {"status": "error", "message": "Unknown endpoint"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            payload = json.loads(raw_body) if raw_body.strip() else {}
            dry_run = bool(payload.get("dry_run", False))

            result = asyncio.run(execute_action(command, payload=payload, dry_run=dry_run))
            self._send_json(200, result)
        except Exception as exc:
            self._send_json(400, {"status": "error", "message": str(exc)})


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Set BRIDGE_API_KEY environment variable before starting server.py", file=sys.stderr)
        sys.exit(1)

    server = ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    print(f"muse-x-bridge HTTP server listening on http://{HOST}:{PORT}")
    server.serve_forever()
