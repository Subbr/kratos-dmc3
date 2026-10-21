#!/usr/bin/env bash
# Abre o DMC3 e entra na missão do save do slot SLOT (padrão 2 = início da Missão 3). Teclas confirmadas
# em 2026-10-21: Enter = Start, K = confirmar (A), L = cancelar (B), A/D = esquerda/direita.
# Requer no CrimsonConfig.json: skipIntro e skipCutscenes = true. Termina com work/shots/game.png.
set -e
cd "$(dirname "$0")/../.."
P='D:\Code\god1_dmc3\tools\win\game.ps1'
g() { powershell.exe -ExecutionPolicy Bypass -File "$P" "$@" >/dev/null; }
g stop || true
powershell.exe -Command "Start-Sleep 3; Get-Process dmcLauncher -ErrorAction SilentlyContinue | Stop-Process" || true
g start
powershell.exe -Command "Start-Sleep 22"
g keys "enter:300 wait:4000"            # aviso de salvamento -> título (cursor em LOAD GAME)
g keys "enter:300 wait:4000"            # -> tela LOAD
for _ in $(seq 11); do                  # lista circular; a posição inicial varia
  tools/win/step.sh "" load_slot >/dev/null
  [ "$(tools/.venv/bin/python -I tools/win/load_slot.py work/shots/load_slot.png)" = "${SLOT:-2}" ] && break
  g keys "d:250 wait:1200"
done
g keys "k:300 wait:2000 a:300 wait:800 k:300 wait:6000"   # confirma, "Yes" (padrão "No"), carrega
g keys "enter:300 wait:8000"            # "Load Successful" -> Mission Select
g keys "k:300 wait:8000"                # missão do save -> menu da missão (cursor em Customize)
g keys "a:300 wait:900 k:300 wait:15000" # Mission Start
tools/win/step.sh "" game
