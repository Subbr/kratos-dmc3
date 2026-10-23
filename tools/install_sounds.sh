#!/usr/bin/env bash
# Copia os sons do GoW1 extraídos da ISO (extracted/gow1/sound, god_of_war_browser: R_PERM.WAD tags 81 "Hero" e
# 69 "GENERAL") para Crimson\sound\kratos\<evento>_<n>.wav, nomes lidos por KratosSound.cpp. Uso: tools/install_sounds.sh
set -e
cd "$(dirname "$0")/.."
S=extracted/gow1/sound
D="Devil May Cry HD Collection/Crimson/sound/kratos"
rm -rf "$D"; mkdir -p "$D"
put() {  # put <evento> <arquivos...>
  local e=$1 n=0; shift
  for f in "$@"; do [ -f "$f" ] && cp "$f" "$D/${e}_$n.wav" && n=$((n + 1)); done
  echo "$e: $n"
}
put swing $S/general/SND_WHOOSHMID_FAST_*.wav $S/general/SND_WHOOSHMID_MEDIUM_*.wav $S/general/SND_CHAINSNAP_A_*.wav
put voice_short $S/hero/H_ATTKS[1-4].wav
put voice_long $S/hero/H_ATTKL[12].wav
put hit $S/general/SND_SWORDHIT_CHEST_*.wav $S/general/SND_ENEMY_GETHIT_S_*.wav
put gun_hit $S/general/SND_BOLT_HIT_*.wav
put hurt $S/hero/H_DMG[1-6].wav
put die $S/hero/DIEVOC1.wav
put jump $S/hero/JUMPVOC[12].wav
put medusa_shot $S/general/SND_MEDUSA_RAY_SHOT_*.wav
put stone $S/general/SND_MEDUSA_TURNTOSTONE_*.wav
put flesh $S/general/SND_MEDUSA_TURNTOFLESH_*.wav
put block $S/general/SND_BLADEBLOCK_*.wav
put step_walk $S/general/SND_FOOTSTEP_STONEWALK_*.wav
put step_run $S/general/SND_FOOTSTEP_STONERUN_*.wav
put land $S/general/SND_FOOTSTEP_STONELAND_*.wav
