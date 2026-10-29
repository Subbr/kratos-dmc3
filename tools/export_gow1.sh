#!/usr/bin/env bash
# Extrai da ISO do GoW1 tudo o que o modo Kratos usa. Uso: tools/export_gow1.sh [saída = extracted/gow1]
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py export ${1:+--out "$1"}
