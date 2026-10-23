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
g keys "enter:300 wait:4000"            # -> tela LOAD (prévia do slot)
dialog() { tools/win/step.sh "" load_dialog >/dev/null; tools/.venv/bin/python -I tools/win/load_slot.py work/shots/load_dialog.png dialog; }
g keys "k:300 wait:2000"                # entra no modo de escolha ("Please specify a file to load")
[ "$(dialog)" != none ] && g keys "l:300 wait:1500"   # se já abriu o diálogo, cancela
for _ in $(seq 11); do                  # lista circular; a posição inicial varia
  tools/win/step.sh "" load_slot >/dev/null
  [ "$(tools/.venv/bin/python -I tools/win/load_slot.py work/shots/load_slot.png)" = "${SLOT:-2}" ] && break
  g keys "d:250 wait:1200"
done
[ "$(tools/.venv/bin/python -I tools/win/load_slot.py work/shots/load_slot.png)" = "${SLOT:-2}" ] || { echo "slot ${SLOT:-2} não selecionado" >&2; exit 1; }
g keys "k:300 wait:2500"                # abre "OK to load this file?" (padrão "No")
for _ in 1 2 3 4; do [ "$(dialog)" != none ] && break; g keys "wait:1000"; done
for _ in 1 2 3; do [ "$(dialog)" = yes ] && break; [ "$(dialog)" = none ] && break; g keys "a:300 wait:1000"; done
[ "$(dialog)" = yes ] || { echo "diálogo de load não chegou em Yes" >&2; exit 1; }
g keys "k:300 wait:6000"
if grep -q '"virtualPad": true' "Devil May Cry HD Collection/Crimson/configs/KratosConfig.json"; then
  # controle virtual (2026-10-22): "Load Successful" fecha com A; o menu da missão só anda no direcional e
  # confirma no Start
  g keys "k:300 wait:8000"              # "Load Successful" -> Mission Select
  g keys "k:300 wait:8000"              # missão do save -> menu da missão (cursor em Customize)
  g keys "left:300 wait:900 enter:300 wait:15000"   # Mission Start
else
  g keys "enter:300 wait:8000"          # "Load Successful" -> Mission Select
  g keys "k:300 wait:8000"              # missão do save -> menu da missão (cursor em Customize)
  g keys "a:300 wait:900 k:300 wait:15000" # Mission Start
fi
tools/win/step.sh "" game
