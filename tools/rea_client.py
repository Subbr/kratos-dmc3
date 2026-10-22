"""Cliente mínimo do servidor MCP (HTTP) do REA, com sessão persistente em work/re/rea_session.json.

Uso: python -I tools/rea_client.py <tool> '<json de argumentos>'   (ex.: open_binary '{"path": "..."}')
     python -I tools/rea_client.py --list
"""
import itertools
import json
import sys
import time
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8765/"  # tools/rea_bridge.py
STATE = Path(__file__).resolve().parent.parent / "work/re/rea_session.json"


def post(payload: dict, session: str | None) -> tuple[dict | None, str | None]:
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
        **({"Mcp-Session-Id": session} if session and session != "bridge" else {})})
    with urllib.request.urlopen(req, timeout=3600) as r:
        sid = r.headers.get("Mcp-Session-Id") or session
        body = r.read().decode()
    if not body.strip():
        return None, sid
    if body.lstrip().startswith("{"):
        return json.loads(body), sid
    msgs = [json.loads(line[5:]) for line in body.splitlines() if line.startswith("data:")]
    return (msgs[-1] if msgs else None), sid


def session() -> str:
    if STATE.exists():
        return json.loads(STATE.read_text())["session"]
    # a ponte é um único cliente; o "session" só marca que o initialize já foi feito
    res, sid = post({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "kratos-dmc3", "version": "1"}}}, None)
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    STATE.write_text(json.dumps({"session": sid or "bridge"}))
    return sid or "bridge"


def main() -> None:
    sid = session()
    if sys.argv[1] == "--list":
        res, _ = post({"jsonrpc": "2.0", "id": int(time.time() * 1000), "method": "tools/list"}, sid)
        for t in res["result"]["tools"]:
            print(t["name"], "-", (t.get("description") or "")[:110].replace("\n", " "))
        return
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    res, _ = post({"jsonrpc": "2.0", "id": int(time.time() * 1000), "method": "tools/call", "params": {"name": sys.argv[1], "arguments": args}}, sid)
    out = res.get("result", res)
    for c in out.get("content", []):
        print(c.get("text", c))
    if "structuredContent" in out and not out.get("content"):
        print(json.dumps(out["structuredContent"], indent=1)[:20000])


if __name__ == "__main__":
    main()
