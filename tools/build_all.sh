#!/usr/bin/env bash
# Regera todos os arquivos do modo Kratos a partir dos dados do usuário (Fase 10, T57):
#   - bases do DMC3/Crimson: work/backup/crimson_override (originais do override do Crimson) e o .nbz do jogo;
#   - assets do GoW1: extracted/gow1 (tools/export_gow1.sh, da ISO do usuário).
# Uso: tools/build_all.sh <pasta de saída>   (ex.: work/build_check; depois comparar com work/install)
set -eu
cd "$(dirname "$0")/.."
OUT=${1:?pasta de saída}; mkdir -p "$OUT"
PY="tools/.venv/bin/python -I"
B=work/backup/crimson_override; U=extracted/dmc3/unpacked; G=extracted/gow1
GLB=$G/hero0/hero_obj.glb; BLADE=$G/weapons/maiblade.glb
FIT="--left-weapon $BLADE --both-hands --blade-bones --flip-edge"
unpack() { [ -d "$U/$2" ] || $PY tools/pac.py unpack "$1" "$U/$2" >/dev/null; }
# Dante original do jogo (sem Crimson): esqueleto de referência de tools/build_motions.py
if [ ! -d "$U/pl000" ]; then
  source config/paths.env; mkdir -p "$U"
  $PY -c 'import sys, zipfile; open(sys.argv[3], "wb").write(zipfile.ZipFile(sys.argv[1]).read(sys.argv[2]))' \
    "$DMC3_NBZ" GData.afs/pl000.pac "$U/pl000.pac"
  unpack "$U/pl000.pac" pl000; rm -f "$U/pl000.pac"
fi

# 1. corpo e roupas do Kratos (T3–T10, T41–T42)
unpack $B/pl000.pac crimson_pl000
$PY tools/kratos_fit.py $GLB $U/crimson_pl000 "$OUT/pl000.pac" $FIT
for n in pl011 pl013 pl015 pl016 pl018; do
  unpack $B/$n.pac base_$n
  $PY tools/kratos_fit.py $GLB $U/base_$n "$OUT/$n.pac" $FIT
done
# 2. Devil Trigger dourado em todas as armas (T22, T32)
for n in pl005 pl006 pl007 pl008 pl009 pl017; do
  unpack $B/$n.pac crimson_$n
  hide=$(ls $U/crimson_$n | grep MOD | grep -v '^001' | paste -sd, - || true)
  # Rage of the Gods: Blades em brasa do GoW1 (maigodblade, nível máximo; T60)
  $PY tools/kratos_fit.py $GLB $U/crimson_$n "$OUT/$n.pac" ${FIT/maiblade/maigodblade} --hide "$hide" --tint 1,0.75,0.2,0.35
done
# 3. armas: Artemis no slot Agni & Rudra (T26); as do Dante escondidas (T8, T45, T49, T50)
unpack $B/plwp_2sword.pac crimson_plwp_2sword
$PY tools/weapon_fit.py $G/weapons/athenablade.glb $U/crimson_plwp_2sword "$OUT/plwp_2sword.pac"
for n in plwp_sword plwp_sword2 plwp_sword3 plwp_gun plwp_shotgun plwp_laser plwp_rifle plwp_grenade plwp_nunchaku plwp_guitar plwp_fight; do
  $PY tools/hide_models.py $B/$n.pac "$OUT/$n.pac" >/dev/null
done
# 4. motions do Kratos (mapping/motions.yaml)
$PY tools/build_motions.py $B "$OUT" --model "$OUT/pl000.pac" >/dev/null
# 4b. motor Kratos (D11): golpes do GoW1 no tempo original + tabela para a DLL (KratosMoves.json)
$PY tools/build_fx.py $G/magic "$OUT/kratos_fx" >/dev/null
$PY tools/build_engine_moves.py $B/pl000_00_2.pac "$OUT/pl000.pac" "$OUT/kratosMoves_pl000_00_2.pac" >/dev/null
# 4c. Kratos do GoW1 desenhado pela DLL (T98): esqueleto, malhas, lâminas e animações originais
$PY tools/build_body.py $G/hero0/hero_obj.glb $G/weapons/maiblade.glb "$OUT/kratos_body/kratos.kbd" >/dev/null
# 5. textos (T38)
$PY tools/build_text.py $B/msg_eng.pac "$OUT/msg_eng.pac" >/dev/null
# 6. artes dos menus com o Kratos (T59, T77; renders de tools/render_menu_art.sh, que precisa do Blender)
[ -f work/install/menu_art/renders/blades_title.png ] || tools/render_menu_art.sh || true
if ls work/install/menu_art/renders/blades_title.png >/dev/null 2>&1; then
  $PY tools/build_menu_art.py "$OUT" >/dev/null && rm -f "$OUT"/*.preview.png
fi
echo "pronto: $(ls "$OUT" | wc -l) arquivos em $OUT"
