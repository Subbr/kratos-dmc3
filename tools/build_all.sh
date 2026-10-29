#!/usr/bin/env bash
# Regera todos os arquivos do modo Kratos. Uso: tools/build_all.sh <pasta de saída>
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py build --out "${1:?pasta de saída}"
