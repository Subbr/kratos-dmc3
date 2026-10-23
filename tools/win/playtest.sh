#!/usr/bin/env bash
# Playtest automático de uma missão pelo Arcade do Crimson (T41): abre o jogo direto na missão, roda uma rotina de
# combate (andar, combo, pulo + ataque, bloqueio, Spiral/Medusa, agarrão, DT), captura a tela a cada fase e confere se
# o jogo segue respondendo. Uso: tools/win/playtest.sh <missão 1–20>  → work/shots/playtest/mNN_*.png e uma linha
# de resumo. Exige virtualPad e, para não morrer, playerReceivedDmgMult 0. O CrimsonConfig original fica em
# work/backup/crimson_override/CrimsonConfig.json.pre_t41.
set -u
cd "$(dirname "$0")/../.."
M=$1; N=$(printf "m%02d" "$M")
P='D:\Code\god1_dmc3\tools\win\game.ps1'
g() { powershell.exe -ExecutionPolicy Bypass -File "$P" "$@" >/dev/null 2>&1; }
LOG="Devil May Cry HD Collection/logs/kratos.txt"
OUT=work/shots/playtest; mkdir -p $OUT; rm -f $OUT/${N}_*.png
tools/.venv/bin/python -I - "$M" <<'PY'
import json, pathlib, sys
p = pathlib.Path("Devil May Cry HD Collection/Crimson/configs/CrimsonConfig.json")
d = json.loads(p.read_text(encoding="utf-8"))
# armas: Rebellion (Blades), Agni & Rudra (Artemis), E&I (Zeus), Spiral (Medusa)
d["Arcade"].update({"enable": True, "mission": int(sys.argv[1]), "mode": 1, "weapons": [0, 2, 5, 8]})
p.write_text(json.dumps(d, indent=4), encoding="utf-8")
PY
g stop; sleep 4; rm -f "$LOG"
g start; sleep 30
alive() { powershell.exe -Command "(Get-Process dmc3 -ErrorAction SilentlyContinue).Responding" 2>/dev/null | tr -d '\r'; }
shot() { g shot "D:\\Code\\god1_dmc3\\work\\shots\\playtest\\${N}_$1.png"; }
status=ok
phase() {  # phase <nome> <teclas>
  [ "$(alive)" = True ] || { status="caiu antes de $1"; return 1; }
  g keys "$2"; shot "$1"
}
phase 0_start "wait:500" &&
phase 1_walk "w:2500 wait:300 d:800 wait:300" &&
phase 2_combo "i:50 wait:220 i:50 wait:220 i:50 wait:700 i:50 wait:220 i:50 wait:700 i:50 wait:700 i:50 wait:220 i:50 wait:220 i:50 wait:900" &&
phase 3_air "k:80 wait:250 i:80 wait:1500 k:80 wait:250 l:60 wait:300 l:60 wait:300 l:60 wait:1500" &&
phase 4_block "l:2500 wait:300 tab:100 wait:1500" &&
phase 5_magic "q:200 wait:900 j:80 wait:1500 q:200 wait:900 j:80 wait:600 j:80 wait:1500" &&
phase 6_dt "u:150 wait:1500 i:50 wait:220 i:50 wait:220 i:50 wait:1200 u:150 wait:800" &&
phase 7_end "w:2000 wait:300 i:50 wait:220 i:50 wait:220 i:50 wait:1500"
[ "$(alive)" = True ] || [ "$status" != ok ] || status="caiu no fim"
c() { grep -c "$1" "$LOG" 2>/dev/null || true; }
echo "$N $status | dano $(c '^dmg\|magia dano') magia $(c '^magic tiro') medusa $(c '^medusa petrificou [1-9]') agarrao $(c '^agarrao') sons $(c '^som') motions $(c '^motion')"
