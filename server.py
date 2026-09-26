#!/usr/bin/env python3
"""
HTTP Server for Vera AI Bot
Implements the 5 challenge endpoints defined in challenge-testing-brief.md:
- GET  /v1/healthz
- GET  /v1/metadata
- POST /v1/context
- POST /v1/tick
- POST /v1/reply
"""

import os
import sys
import time
import json
from pathlib import Path

# Ensure script directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from bot import store, compose, handle_reply

START_TIME = time.time()

class BotRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/v1/healthz", "/healthz", "/"):
            uptime = int(time.time() - START_TIME)
            self._send_json(200, {
                "status": "ok",
                "uptime_seconds": uptime,
                "contexts_loaded": {
                    "category": len(store.categories),
                    "merchant": len(store.merchants),
                    "customer": len(store.customers),
                    "trigger": len(store.triggers)
                }
            })
            return

        if self.path in ("/v1/metadata", "/metadata"):
            self._send_json(200, {
                "team_name": "Team Vera Elite",
                "team_members": ["Antigravity"],
                "model": "rule-based-frontier-hybrid",
                "approach": "Deterministic 4-context semantic composer with automated anti-auto-reply, instant intent execution handoff, and zero-hallucination factual grounding",
                "contact_email": "vera-team@magicpin.in",
                "version": "1.0.0",
                "submitted_at": datetime.utcnow().isoformat() + "Z"
            })
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception as e:
            self._send_json(400, {"accepted": False, "reason": "invalid_json", "details": str(e)})
            return

        if self.path in ("/v1/context", "/context"):
            scope = body.get("scope")
            context_id = body.get("context_id")
            version = body.get("version", 1)
            payload = body.get("payload", {})

            if not (scope and context_id):
                self._send_json(400, {"accepted": False, "reason": "missing_required_fields"})
                return

            accepted = store.set(scope, context_id, version, payload)
            if not accepted:
                current_v = store.versions.get((scope, context_id), version)
                self._send_json(409, {"accepted": False, "reason": "stale_version", "current_version": current_v})
                return

            self._send_json(200, {
                "accepted": True,
                "ack_id": f"ack_{context_id}_v{version}",
                "stored_at": datetime.utcnow().isoformat() + "Z"
            })
            return

        if self.path in ("/v1/tick", "/tick"):
            available_triggers = body.get("available_triggers", [])
            actions = []
            for trg_id in available_triggers:
                trg = store.get_trigger(trg_id)
                if not trg:
                    continue
                mid = trg.get("merchant_id")
                cid = trg.get("customer_id")
                merchant = store.get_merchant(mid) if mid else None
                if not merchant:
                    continue
                cat_slug = merchant.get("category_slug", "")
                category = store.get_category(cat_slug) or {"slug": cat_slug}
                customer = store.get_customer(cid) if cid else None

                composed = compose(category, merchant, trg, customer)
                actions.append({
                    "conversation_id": f"conv_{mid}_{trg_id}",
                    "merchant_id": mid,
                    "customer_id": cid,
                    "send_as": composed.get("send_as", "vera"),
                    "trigger_id": trg_id,
                    "template_name": "vera_proactive_v1",
                    "template_params": [merchant.get("identity", {}).get("name", ""), cat_slug],
                    "body": composed.get("body", ""),
                    "cta": composed.get("cta", "binary"),
                    "suppression_key": composed.get("suppression_key", f"suppress:{trg_id}"),
                    "rationale": composed.get("rationale", "")
                })

            self._send_json(200, {"actions": actions})
            return

        if self.path in ("/v1/reply", "/reply"):
            conv_id = body.get("conversation_id", "default_conv")
            mid = body.get("merchant_id")
            cid = body.get("customer_id")
            from_role = body.get("from_role", "merchant")
            message = body.get("message", "")
            turn = body.get("turn_number", 1)

            resp = handle_reply(conv_id, mid, cid, from_role, message, turn)
            self._send_json(200, resp)
            return

        self._send_json(404, {"error": "Not found"})

    def log_message(self, format, *args):
        # Silence default request logging to keep console clean
        pass

def run(port: int = 8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, BotRequestHandler)
    print(f"Bot server listening on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    env_port = os.environ.get("PORT")
    port = int(env_port) if env_port else (int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
    run(port)
