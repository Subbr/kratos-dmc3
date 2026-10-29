#!/usr/bin/env bash
# Instala os sons do GoW1 em Crimson\sound\kratos. Uso: tools/install_sounds.sh
# A lógica está em tools/kratos_install.py (a mesma do instalador do Windows).
set -eu
cd "$(dirname "$0")/.."
exec tools/.venv/bin/python -X utf8 tools/kratos_install.py sounds
