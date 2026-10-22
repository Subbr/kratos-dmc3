#!/usr/bin/env bash
# Teste de acerto (T18): entra na Missão 3, chama os inimigos e faz combos; o log da DLL (logDamage) registra
# cada dano com a motion. Uso: tools/win/combo_test.sh <nome>  → work/shots/<nome>_kratos.txt
# (resumo: python -I tools/win/damage_report.py work/shots/<nome>_kratos.txt)
set -e
cd "$(dirname "$0")/../.."
LOG="Devil May Cry HD Collection/logs/kratos.txt"
rm -f "$LOG"
tools/win/to_mission.sh >/dev/null
powershell.exe -Command "Start-Sleep 5"
tools/win/burst.sh "s:1800" 4 600 "$1_walk" >/dev/null          # o 1º avanço dispara a entrada dos inimigos
powershell.exe -Command "Start-Sleep 4"
C1="i:50 wait:220 i:50 wait:220 i:50 wait:900"                      # combo 1 (3→4→5)
C2="i:50 wait:220 i:50 wait:700 i:50 wait:220 i:50 wait:900"        # combo 2 (pausa)
tools/win/burst.sh "$C1 $C1 $C2 $C1 $C2 $C1 $C1 $C2" 30 400 "$1_combo" >/dev/null
tr -d '\r' < "$LOG" > "work/shots/$1_kratos.txt"
grep -c "^dmg" "work/shots/$1_kratos.txt" || true
