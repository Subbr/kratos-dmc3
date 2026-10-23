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
  $PY tools/kratos_fit.py $GLB $U/crimson_$n "$OUT/$n.pac" $FIT --hide "$hide" --tint 1,0.75,0.2,0.35
done
# 3. armas: Artemis no slot Agni & Rudra (T26); as do Dante escondidas (T8, T45, T49, T50)
unpack $B/plwp_2sword.pac crimson_plwp_2sword
$PY tools/weapon_fit.py $G/weapons/athenablade.glb $U/crimson_plwp_2sword "$OUT/plwp_2sword.pac"
for n in plwp_sword plwp_sword2 plwp_sword3 plwp_gun plwp_shotgun plwp_laser plwp_rifle plwp_grenade plwp_nunchaku plwp_guitar plwp_fight; do
  $PY tools/hide_models.py $B/$n.pac "$OUT/$n.pac" >/dev/null
done
# 4. motions do Kratos (mapping/motions.yaml)
$PY tools/build_motions.py $B "$OUT" --model "$OUT/pl000.pac" >/dev/null
# 5. textos (T38)
$PY tools/build_text.py $B/msg_eng.pac "$OUT/msg_eng.pac" >/dev/null
# 6. artes dos menus com o Kratos (T59; precisa dos renders do blender/scripts/render_kratos.py)
if ls work/install/menu_art/renders/pose_10_idleCombat.png >/dev/null 2>&1; then
  $PY tools/build_menu_art.py "$OUT" >/dev/null && rm -f "$OUT"/*.preview.png
fi
echo "pronto: $(ls "$OUT" | wc -l) arquivos em $OUT"
