#!/usr/bin/env bash
# Motions de um tiro de cada arma de fogo (T49): Missão 3 com testWeapons (E&I + Spiral, todas liberadas); LT percorre
# E&I → Shotgun → Artemis → Spiral. Uso: tools/win/gun_probe.sh → work/shots/gun_probe.txt
set -u
cd "$(dirname "$0")/../.."
W=$(wslpath -w "$PWD")   # raiz do projeto no Windows (sem caminho fixo)
CD="Devil May Cry HD Collection/Crimson/configs"; LOG="Devil May Cry HD Collection/logs/kratos.txt"
for f in KratosConfig CrimsonConfigGameplay; do cp "$CD/$f.json" "$CD/$f.json.probe_bak"; done
trap 'powershell.exe -ExecutionPolicy Bypass -File "$W\tools\win\game.ps1" stop >/dev/null; sleep 3; for f in KratosConfig CrimsonConfigGameplay; do mv -f "$CD/$f.json.probe_bak" "$CD/$f.json"; done' EXIT
tools/.venv/bin/python -I - <<'PY'
import json, pathlib
cd = pathlib.Path("Devil May Cry HD Collection/Crimson/configs")
p = cd / "KratosConfig.json"; d = json.loads(p.read_text())
d.update({"logDamage": True, "testWeapons": True, "testRangedWeapon": 8, "magicShotCost": 1.0, "poseidonCost": 1.0,
          "medusaCost": 1.0, "hadesCost": 1.0})
p.write_text(json.dumps(d, indent=4))
p = cd / "CrimsonConfigGameplay.json"; d = json.loads(p.read_text())
d["Cheats"]["Damage"]["playerReceivedDmgMult"] = 0.0
p.write_text(json.dumps(d, indent=4))
PY
tools/win/to_mission.sh >/dev/null 2>&1
g() { powershell.exe -ExecutionPolicy Bypass -File "$W\tools\win\game.ps1" keys "$1" >/dev/null 2>&1; }
OUT=work/shots/gun_probe.txt; : > $OUT
for gun in zeus poseidon hades medusa; do
  for mode in chao travado ar andar; do
    rm -f "$LOG"
    case $mode in
      chao) tools/win/burst.sh "j:80" 8 110 gun_$gun >/dev/null; g "wait:1000" ;;   # folha do disparo
      travado) g "+n wait:300 j:80 wait:1800 -n wait:300" ;;
      ar) g "k:80 wait:250 j:80 wait:1500" ;;
      andar) g "+n wait:300 +d wait:1200 -d +s wait:800 -s +w wait:800 -w -n wait:300" ;;   # locomoção travada (T53)
    esac
    echo "$gun $mode: $(grep '^motion' "$LOG" 2>/dev/null | cut -d' ' -f2 | tr '\n' ' ')" >> $OUT
  done
  g "q:200 wait:1200"
done
cat $OUT
