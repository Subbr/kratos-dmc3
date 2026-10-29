#!/usr/bin/env bash
# Junta os arquivos-base do DMC3/Crimson em work/backup/crimson_override. Uso: tools/prepare_bases.sh
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py bases
