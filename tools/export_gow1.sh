#!/usr/bin/env bash
# Extrai da ISO do GoW1 do usuário tudo o que o modo Kratos usa (Fase 10, T57), pelo god_of_war_browser
# (vendor/gowb_bin; docs/formats/gow-wad.md): Kratos e armas (glb), vozes e sons (WAV), HUD (PNG).
# Uso: tools/export_gow1.sh [pasta de saída = extracted/gow1]   (ISO em config/paths.env: GOW1_ISO)
set -eu
cd "$(dirname "$0")/.."
source config/paths.env
OUT=${1:-extracted/gow1}; mkdir -p "$OUT"/{hero0,weapons,sound/hero,sound/general,hud}
URL=http://127.0.0.1:8000
started=""
if ! curl -s -m 5 $URL/json/pack >/dev/null; then
  (cd vendor/god_of_war_browser && ../gowb_bin/god_of_war_browser -iso "$GOW1_ISO" -ps ps2 -gowversion 1 -i 127.0.0.1:8000 >/dev/null 2>&1 &)
  started=1
  for _ in $(seq 60); do curl -s -m 5 $URL/json/pack >/dev/null && break; sleep 2; done
fi
tools/.venv/bin/python -I - "$OUT" <<'PY'
import base64, io, json, pathlib, re, sys, urllib.request
out = pathlib.Path(sys.argv[1]); url = "http://127.0.0.1:8000"
def get(path): return urllib.request.urlopen(url + path, timeout=600).read()
def tags(wad):
    d = json.loads(get(f"/json/pack/{wad}"))
    nodes = d["Nodes"].values() if isinstance(d["Nodes"], dict) else d["Nodes"]
    return {n["Tag"]["Name"]: n["Tag"]["Id"] for n in nodes}
# modelos: (WAD, tag, arquivo)
for wad, name, dst in [("R_HERO0.WAD", "hero", "hero0/hero_obj.glb"), ("R_WPN0_0.WAD", "maiblade", "weapons/maiblade.glb"),
                       ("ATHN08C.WAD", "athenablade", "weapons/athenablade.glb")]:
    t = tags(wad)
    if name not in t: print("não achado:", wad, name); continue
    (out / dst).write_bytes(get(f"/action/{wad}/{t[name]}/gltf")); print(dst)
# vozes (banco "Hero") e sons de combate (banco "GENERAL") do R_PERM
t = tags("R_PERM.WAD")
hero = json.loads(get(f"/json/pack/R_PERM.WAD/{t['Hero']}"))["Data"]
for s in hero["Sounds"]:
    (out / "sound/hero" / f"{s['Name']}.wav").write_bytes(get(f"/action/R_PERM.WAD/{t['Hero']}/wav?snd={s['Name']}"))
gen = json.loads(get(f"/json/pack/R_PERM.WAD/{t['GENERAL']}"))["Data"]
want = ["WHOOSH", "CHAIN", "BLADE", "SWORDHIT", "SWORD_", "ENEMY_GETHIT", "PICKUPS_ORBS", "MEDUSA", "BOLT_HIT",
        "BERZBLADE", "IG_MAGICOUT", "ROCKHIT", "FOOTSTEP_STONE"]
for s in gen["Sounds"]:
    if not any(w in s["Name"] for w in want): continue
    seen, k = set(), 0
    for c in gen["Bank"]["BankSounds"][s["StreamId"]]["Commands"]:
        r = c.get("SampleRef")
        if not r or (r["AdpcmOffset"], r["AdpcmSize"]) in seen: continue
        seen.add((r["AdpcmOffset"], r["AdpcmSize"]))
        (out / "sound/general" / f"{s['Name']}_{k}.wav").write_bytes(
            get(f"/action/R_PERM.WAD/{t['GENERAL']}/smpd?offset={r['AdpcmOffset']}&size={r['AdpcmSize']}")); k += 1
# sons de magia soltos na ISO (T58): Rage e Poseidon [HIPÓTESE pelo nome]
(out / "sound/magic").mkdir(parents=True, exist_ok=True)
for name in ("POSMAG06.VAG", "RAGEMIME.VAG"):
    (out / "sound/magic" / name.replace(".VAG", ".wav")).write_bytes(get(f"/dump/pack/{name}/wav"))
# HUD: TXR_HUD* (PNG embutido no JSON de cada textura)
for name, tid in t.items():
    if not re.match(r"TXR_HUD\d+$", name): continue
    imgs = (json.loads(get(f"/json/pack/R_PERM.WAD/{tid}")).get("Data") or {}).get("Images") or []
    if imgs: (out / "hud" / f"{name}.png").write_bytes(base64.b64decode(imgs[0]["Image"]))
print("ok")
PY
# pelo nome do processo: "pkill -f" casaria com a linha de comando deste próprio shell
[ -n "$started" ] && kill $(pgrep -x god_of_war_brow) 2>/dev/null || true
