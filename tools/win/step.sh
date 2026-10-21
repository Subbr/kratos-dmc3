#!/usr/bin/env bash
# Aperta teclas no jogo e salva uma miniatura da tela: tools/win/step.sh "<seq>" <nome>
set -e
cd "$(dirname "$0")/../.."
P='D:\Code\god1_dmc3\tools\win\game.ps1'
[ -n "$1" ] && powershell.exe -ExecutionPolicy Bypass -File "$P" keys "$1" >/dev/null
powershell.exe -ExecutionPolicy Bypass -File "$P" shot "D:\\Code\\god1_dmc3\\work\\shots\\$2.png" >/dev/null
tools/.venv/bin/python -I tools/win/thumb.py "work/shots/$2.png" "work/shots/$2_t.png" 640
echo "work/shots/$2_t.png"
