"""Ponte HTTP -> MCP stdio do REA: mantém um `rea --mcp` vivo (a análise do Ghidra fica carregada entre consultas).

Uso: python -I tools/rea_bridge.py   (escuta em 127.0.0.1:8765; POST com uma mensagem JSON-RPC, resposta JSON-RPC)
"""
import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
proc = subprocess.Popen([str(ROOT / "tools/rea.sh"), "--mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=open(ROOT / "work/re/rea_stderr.log", "ab"), text=True, bufsize=1)
lock = threading.Lock()
pending: dict = {}
cond = threading.Condition()


def reader() -> None:
    for line in proc.stdout:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" in msg and ("result" in msg or "error" in msg):
            with cond:
                pending[msg["id"]] = msg
                cond.notify_all()


threading.Thread(target=reader, daemon=True).start()


class H(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        msg = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with lock:
            proc.stdin.write(json.dumps(msg) + "\n")
            proc.stdin.flush()
        out = b""
        if "id" in msg:
            with cond:
                cond.wait_for(lambda: msg["id"] in pending)
                out = json.dumps(pending.pop(msg["id"])).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a) -> None:
        pass


ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
