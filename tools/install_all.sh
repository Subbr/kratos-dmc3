#!/usr/bin/env bash
# Instala no jogo (override, configs, efeitos, corpo, sons, HUD, DLL). Uso: tools/install_all.sh [--check | --restore]
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
case ${1:-} in --check) c=check ;; --restore) c=restore ;; *) c=install ;; esac
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py $c
