#!/usr/bin/env bash
# Instala a arte e o filme do HUD do GoW1 em Crimson\huds\kratos. Uso: tools/install_hud.sh
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py hud
