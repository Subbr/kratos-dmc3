#!/usr/bin/env bash
# Descobre as motions de uma arma de corpo a corpo (T45): Missão 3 (slot 2) com a arma como 2ª de corpo a corpo
# (testWeapons + testMeleeWeapon), troca com RT e roda cada comando separado, listando as motions que ele tocou.
# Uso: tools/win/motion_probe.sh <WEAPON::* 1–4> [estilo -1/0/…]  → work/shots/probe_w<N>.txt
# O RT percorre todas as armas liberadas (Rebellion → Cerberus → Agni → Nevan → Beowulf): aperta RT <N> vezes.
set -u
cd "$(dirname "$0")/../.."
ROOTW=$(wslpath -w "$PWD")   # raiz do projeto no Windows (sem caminho fixo)
W=$1; ST=${2:--1}
CD="Devil May Cry HD Collection/Crimson/configs"; LOG="Devil May Cry HD Collection/logs/kratos.txt"
for f in KratosConfig CrimsonConfigGameplay; do cp "$CD/$f.json" "$CD/$f.json.probe_bak"; done
trap 'powershell.exe -ExecutionPolicy Bypass -File "$ROOTW\tools\win\game.ps1" stop >/dev/null; sleep 3; for f in KratosConfig CrimsonConfigGameplay; do mv -f "$CD/$f.json.probe_bak" "$CD/$f.json"; done' EXIT
tools/.venv/bin/python -I - "$W" "$ST" <<'PY'
import json, pathlib, sys
cd = pathlib.Path("Devil May Cry HD Collection/Crimson/configs")
p = cd / "KratosConfig.json"; d = json.loads(p.read_text())
d.update({"logDamage": True, "testWeapons": True, "testMeleeWeapon": int(sys.argv[1]), "testStyle": int(sys.argv[2])})
p.write_text(json.dumps(d, indent=4))
p = cd / "CrimsonConfigGameplay.json"; d = json.loads(p.read_text())
d["Cheats"]["Damage"]["playerReceivedDmgMult"] = 0.0
p.write_text(json.dumps(d, indent=4))
PY
tools/win/to_mission.sh >/dev/null 2>&1
g() { powershell.exe -ExecutionPolicy Bypass -File "$ROOTW\tools\win\game.ps1" keys "$1" >/dev/null 2>&1; }
RT=""; for _ in $(seq "$W"); do RT="$RT e:200 wait:1200"; done
g "s:1800 wait:5000 $RT"
OUT=work/shots/probe_w$W${2:+_s$2}.txt; : > $OUT
probe() {  # probe <nome> <teclas>
  rm -f "$LOG"; g "$2 wait:1500"
  echo "$1: $(grep '^motion' "$LOG" 2>/dev/null | cut -d' ' -f2 | tr '\n' ' ')" >> $OUT
}
rm -f "$LOG"
tools/win/burst.sh "i:50 wait:220 i:50 wait:220 i:50 wait:220 i:50" 10 130 probe_w$W >/dev/null   # folha do combo
echo "combo: $(grep '^motion' "$LOG" 2>/dev/null | cut -d' ' -f2 | tr '\n' ' ') | acertos $(grep -c '^acerto' "$LOG")" >> $OUT
probe pausa "i:50 wait:220 i:50 wait:700 i:50 wait:220 i:50 wait:220 i:50"
probe frente "+n +w wait:120 i:80 wait:900 -w -n"
probe tras "+n +s wait:120 i:80 wait:900 -s -n"
probe segurar "i:900"
probe ar "k:80 wait:250 i:60 wait:250 i:60 wait:250 i:60 wait:900"
probe ar_tras "k:80 wait:250 +n +s i:80 wait:900 -s -n"
probe estilo "l:80 wait:900 +n +w l:80 -w -n wait:900"
probe estilo_tras "+n +s wait:120 l:80 wait:900 -s -n"
probe estilo_ar "k:80 wait:250 l:60 wait:300 l:60 wait:300 l:60 wait:900"
probe estilo_segurar "l:1200 wait:600"
# PROBE_BACK=1: volta para a arma inicial (RT de novo) e captura um combo (T73: lâminas voltam?)
if [ -n "${PROBE_BACK:-}" ]; then g "e:200 wait:1500"; tools/win/burst.sh "i:50 wait:220 i:50" 6 130 probe_back >/dev/null; fi
cat $OUT
