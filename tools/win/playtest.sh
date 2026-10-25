#!/usr/bin/env bash
# Playtest automático de uma missão pelo Arcade do Crimson (T41): abre o jogo direto na missão, roda uma rotina de
# combate (andar, combo, pulo + ataque, bloqueio, Spiral/Medusa, agarrão, DT), captura a tela a cada fase e confere se
# o jogo segue respondendo. Uso: [BOSS=1] tools/win/playtest.sh <missão 1–20>  → work/shots/playtest/mNN_*.png e
# uma linha de resumo. ROUTINE=moves = sprint/troca de estilo/taunt/Drive (T76). BOSS=1 liga o Boss Rush do Crimson (nasce na sala do chefe; T43) e usa a rotina de chefe.
# Exige virtualPad. Liga logDamage e playerReceivedDmgMult 0 durante o teste; os três configs voltam ao fim.
set -u
cd "$(dirname "$0")/../.."
W=$(wslpath -w "$PWD")   # raiz do projeto no Windows (sem caminho fixo)
M=$1; N=$(printf "%s%02d" "$([ "${BOSS:-0}" = 1 ] && echo b || echo m)" "$M")
P="$W\tools\win\game.ps1"
g() { powershell.exe -ExecutionPolicy Bypass -File "$P" "$@" >/dev/null 2>&1; }
LOG="Devil May Cry HD Collection/logs/kratos.txt"
CD="Devil May Cry HD Collection/Crimson/configs"
for f in CrimsonConfig KratosConfig CrimsonConfigGameplay; do cp "$CD/$f.json" "$CD/$f.json.playtest_bak"; done
# o Arcade e as flags de teste não ficam ligados depois do teste
trap 'g stop; sleep 3; for f in CrimsonConfig KratosConfig CrimsonConfigGameplay; do mv -f "$CD/$f.json.playtest_bak" "$CD/$f.json"; done' EXIT
OUT=work/shots/playtest; mkdir -p $OUT; rm -f $OUT/${N}_*.png
tools/.venv/bin/python -I - "$M" "${BOSS:-0}" <<'PY'
import json, pathlib, sys
cd = pathlib.Path("Devil May Cry HD Collection/Crimson/configs")
def edit(name, fn):
    p = cd / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d, indent=4), encoding="utf-8")
def crimson(d):
    # armas: Rebellion (Blades), Agni & Rudra (Artemis), E&I (Zeus), Spiral (Medusa)
    d["Arcade"].update({"enable": True, "mission": int(sys.argv[1]), "mode": 1, "weapons": [0, 2, 5, 8]})
    d["BossRush"]["enable"] = sys.argv[2] == "1"
edit("CrimsonConfig", crimson)
edit("KratosConfig", lambda d: d.update({"logDamage": True, "virtualPad": True}))  # a config do LG volta no fim
def gameplay(d):
    d["Cheats"]["Damage"]["playerReceivedDmgMult"] = 0.0
edit("CrimsonConfigGameplay", gameplay)
PY
g stop; sleep 4; rm -f "$LOG"
g start; sleep 30
alive() { powershell.exe -Command "(Get-Process dmc3 -ErrorAction SilentlyContinue).Responding" 2>/dev/null | tr -d '\r'; }
shot() { g shot "$W\\work\\shots\\playtest\\${N}_$1.png"; }
status=ok
phase() {  # phase <nome> <teclas>
  [ "$(alive)" = True ] || { status="caiu antes de $1"; return 1; }
  g keys "$2"; shot "$1"
}
if [ "${BOSS:-0}" = 1 ]; then
  # chefe: trava + frente + ataque (Stinger) fecha a distância; combos, Medusa, agarrão e DT, em ciclos
  STING="+n +w wait:120 i:80 wait:600 -w -n"
  CMB="i:50 wait:220 i:50 wait:220 i:50 wait:700"
  phase 0_start "wait:2000 +n j:80 wait:500 j:80 wait:500 j:80 wait:500 j:80 wait:500 -n" &&
  phase 1_sting "$STING $CMB $STING $CMB" &&
  phase 2_magic "q:200 wait:900 q:200 wait:900 q:200 wait:900 +n j:80 wait:1200 j:80 wait:1200 -n" &&
  phase 3_grab "$STING $CMB tab:100 wait:1500 $STING tab:100 wait:1500" &&
  phase 4_dt "u:150 wait:1200 $STING $CMB $STING $CMB u:150 wait:800" &&
  phase 5_air "$STING k:80 wait:250 i:80 wait:1200 $STING $CMB" &&
  phase 6_more "$STING $CMB $STING $CMB $STING $CMB" &&
  phase 7_end "$STING $CMB wait:1500"
elif [ "${ROUTINE:-}" = engine ]; then
  # motor Kratos (D11): 1º ataque prepara o acerto sintético (golpe do Dante), depois combos do motor com capturas
  phase 0_start "w:1200 wait:9000 enter:100 wait:3000" &&
  phase 1_prime "i:50 wait:1500 w:600 wait:300" &&
  tools/win/burst.sh "i:50 wait:300 i:50 wait:300 i:50 wait:300 i:50 wait:300 i:50 wait:1500" 20 130 engine_combo >/dev/null &&
  phase 2_after "wait:300" &&
  tools/win/burst.sh "w:500 i:50 wait:300 i:50 wait:300 l:50 wait:1800" 16 130 engine_combo2 >/dev/null &&
  phase 3_wait "wait:300" &&
  for k in 1 2 3 4 5 6; do phase 4_loop$k "i:50 wait:300 i:50 wait:300 i:50 wait:900 l:50 wait:300 i:50 wait:300 l:50 wait:1200" || break; done
elif [ "${ROUTINE:-}" = moves ]; then
  # golpes que o Crimson toca de arquivos próprios (T76): sprint, troca de estilo parado, taunt e Drive
  phase 0_start "w:1200 wait:9000 enter:100 wait:3000" &&   # o 1º avanço dispara a cena dos inimigos
  phase 1_sprint "+w wait:4000" &&                          # captura ainda correndo (sprint do Crimson, 0/20)
  phase 2_style "-w wait:1200 up:100 wait:1500 right:100 wait:1500 down:100 wait:1500 left:100 wait:1500" &&
  phase 3_taunt "tab:100 wait:2500 tab:100 wait:2500" &&
  phase 4_drive "+n +w wait:120 i:80 wait:200 -w s:100 w:100 i:80 wait:1800 -n i:50 wait:200 s:100 w:100 i:80 wait:1800" &&
  phase 5_back "q:200 wait:600 +n s:150 l:80 wait:1500 -n" &&
  phase 6_end "w:1500 wait:300 i:50 wait:220 i:50 wait:1500"
else
phase 0_start "wait:500" &&
phase 1_walk "w:2500 wait:300 d:800 wait:300" &&
phase 2_combo "i:50 wait:220 i:50 wait:220 i:50 wait:700 i:50 wait:220 i:50 wait:700 i:50 wait:700 i:50 wait:220 i:50 wait:220 i:50 wait:900" &&
phase 3_air "k:80 wait:250 i:80 wait:1500 k:80 wait:250 l:60 wait:300 l:60 wait:300 l:60 wait:1500" &&
phase 4_block "l:2500 wait:300 tab:100 wait:1500" &&
phase 5_magic "q:200 wait:900 j:80 wait:1500 q:200 wait:900 j:80 wait:600 j:80 wait:1500" &&
phase 6_dt "u:150 wait:1500 i:50 wait:220 i:50 wait:220 i:50 wait:1200 u:150 wait:800" &&
phase 7_end "w:2000 wait:300 i:50 wait:220 i:50 wait:220 i:50 wait:1500"
fi
[ "$(alive)" = True ] || [ "$status" != ok ] || status="caiu no fim"
c() { grep -c "$1" "$LOG" 2>/dev/null || true; }
echo "$N${BOSS:+ chefe} $status | acertos $(c '^acerto') dano $(c '^dmg\|magia dano') magia $(c '^magic tiro') medusa $(c '^medusa petrificou [1-9]') agarrao $(c '^agarrao') sons $(c '^som') motions $(c '^motion')"
