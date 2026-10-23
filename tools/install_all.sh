#!/usr/bin/env bash
# Instala no override (data/dmc3/GData.afs) tudo o que o modo Kratos usa hoje, a partir de work/install (T52).
# Uso: tools/install_all.sh [--check | --restore]
#   (sem opção) copia; --check só compara e lista o que difere; --restore devolve os originais do Crimson
#   guardados em work/backup/crimson_override (o que não tem backup é apagado: não existia no Crimson).
# Sons, HUD e DLL: tools/install_sounds.sh, tools/install_hud.sh, tools/win/install_crimson_dll.sh.
set -eu
cd "$(dirname "$0")/.."
O="Devil May Cry HD Collection/data/dmc3/GData.afs"; B=work/backup/crimson_override; I=work/install
MANIFEST=(
  "$I/motions_v18/*.pac"
  "$I/kratos_v10/pl000.pac"
  "$I/kratos_costumes_v1/*.pac"
  "$I/kratos_dt_v2/*.pac"
  "$I/kratos_dt_v1/plwp_sword2.pac"
  "$I/kratos_v5/plwp_sword.pac"
  "$I/artemis_v1/plwp_2sword.pac"
  "$I/weapons_hidden_v1/*.pac"
  "$I/text_v1/msg_eng.pac"
)
mode=${1:-install}; diff=0
for pat in "${MANIFEST[@]}"; do
  for src in $pat; do
    n=$(basename "$src"); dst="$O/$n"
    case $mode in
      --check) cmp -s "$src" "$dst" || { echo "difere: $n ($src)"; diff=$((diff + 1)); } ;;
      --restore) if [ -f "$B/$n" ]; then cp "$B/$n" "$dst"; else rm -f "$dst"; fi ;;
      install)
        [ -f "$dst" ] && [ ! -f "$B/$n" ] && cmp -s "$dst" "$src" || true
        if [ -f "$dst" ] && [ ! -f "$B/$n" ] && ! cmp -s "$dst" "$src"; then
          echo "sem backup de $n (original do Crimson?): copiando para $B" ; cp "$dst" "$B/$n"; (cd "$B" && sha256sum "$n" >> SHA256SUMS)
        fi
        cp "$src" "$dst" ;;
    esac
  done
done
[ "$mode" = --check ] && echo "$diff arquivo(s) diferente(s)"
true
