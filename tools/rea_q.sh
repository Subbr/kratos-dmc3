#!/usr/bin/env bash
# Consulta o REA (ponte em 127.0.0.1:8765) e imprime só o resultado: tools/rea_q.sh <ferramenta> '<json>'
cd "$(dirname "$0")/.."
tools/.venv/bin/python -I tools/rea_client.py "$1" "${2:-{\}}" | tools/.venv/bin/python -I -c "
import json, sys
t = sys.stdin.read()
try:
    d = json.loads(t)
except ValueError:
    print(t[:4000]); sys.exit()
r = d.get('raw_result', d.get('result', d))
print(r['value'] if isinstance(r, dict) and 'value' in r else (r if isinstance(r, str) else json.dumps(r, indent=1)))"
