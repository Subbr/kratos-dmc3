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
# T79 (transcrição local com Whisper, extracted/gow1/sound/transcripts.jsonl): o RAGEMIME é um deus narrando ("Let the
# rage of the gods drive your blades, Kratos") e o POSMAG06 é "Go with the gods, Kratos!" — trocados pelos sons de jogo.
put rage $S/all/STAINVOC_VAG.wav         # rugido do Kratos ("RAAARGH") [HIPÓTESE: voz do Kratos, conferir de ouvido]
put rage_fx $S/general/SND_TRANSFORM_LP_0.wav
put poseidon $S/general/SND_LIGHTNING360_START_0.wav $S/general/SND_LIGHTNING360_BOLT_1.wav  # Poseidon's Rage = Lightning 360
put zeus $S/general/SND_BOLT_FIRE_0.wav
put hades $S/general/SND_RAISEDEAD_SHOT_0.wav
put grab $S/all/PUSHGRNT_VAG.wav $S/general/SND_KICKCHARGEVO_LP_0.wav $S/general/SND_MAI_STRUGGLEVO_LP_3.wav
# falas do Kratos no começo da luta com chefe, recortadas do áudio original (sem gerar nada; regra 5)
cut() {  # cut <origem> <início s> <duração s> <destino>
  ffmpeg -v error -y -i "$1" -ss "$2" -t "$3" -ac 1 -af "afade=t=out:st=$(awk "BEGIN{print $3 - 0.25}"):d=0.25" "$4"
}
mkdir -p "$S/cut"
cut $S/all/A01HL17_VPK.wav 0 5.3 $S/cut/boss_hades.wav     # "Foul beast! I will send you back to the depths of Hades!"
cut $S/all/A08HL02A_VAG.wav 5.1 2.2 $S/cut/boss_demons.wav # "I will put these demons down!"
put boss_start $S/cut/boss_hades.wav $S/cut/boss_demons.wav
# T95: sons dos golpes pelo nome que a tabela de combate do GoW1 pede (evento 3/29): banco GENERAL inteiro em sfx\
# e as vozes do banco Hero com os nomes de evento (SND_HERO_ATTKVOC_SHORT = H_ATTKS1–4 etc.)
X="$D/sfx"; mkdir -p "$X"
cp $S/general/*.wav "$X/"
alias_voice() {  # alias_voice <nome do evento> <arquivos do banco Hero>
  local n=0 e=$1; shift
  for f in "$@"; do [ -f "$f" ] && cp "$f" "$X/${e}_$n.wav" && n=$((n + 1)); done
}
for e in SND_HERO_ATTKVOC_SHORT SND_HERO_ATKVOC_SHORT_A; do alias_voice $e $S/hero/H_ATTKS[1-4].wav; done
for e in SND_HERO_ATTKVOC_LONG SND_HERO_ATKVOC_LONG_A; do alias_voice $e $S/hero/H_ATTKL[12].wav; done
for e in SND_HERO_GETHITVOC SND_HERO_GETHITVOC_A; do alias_voice $e $S/hero/H_DMG[1-6].wav; done
alias_voice SND_HERO_DIEVOC $S/hero/DIEVOC1.wav
echo "sfx: $(ls "$X" | wc -l)"
