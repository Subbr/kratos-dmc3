#!/usr/bin/env bash
# Instala no override (data/dmc3/GData.afs) tudo o que o modo Kratos usa, a partir de work/install/release
# (gerada por tools/build_all.sh; T52, T57).
# Uso: tools/install_all.sh [--check | --restore]
#   (sem opção) copia; --check só compara e lista o que difere; --restore devolve os originais do Crimson
#   guardados em work/backup/crimson_override (o que não tem backup é apagado: não existia no Crimson).
# Sons, HUD e DLL: tools/install_sounds.sh, tools/install_hud.sh, tools/win/install_crimson_dll.sh.
set -eu
cd "$(dirname "$0")/.."
O="Devil May Cry HD Collection/data/dmc3/GData.afs"; B=work/backup/crimson_override; I=work/install
# tudo sai de tools/build_all.sh (T57): uma pasta só
MANIFEST=(
  "$I/release/*.pac"
)
# arquivos que o Crimson não instala (só nós): nunca viram "original do Crimson" no backup (T77: o id7168 do T59 virou)
OURS=" id7168.pac "
mode=${1:-install}; diff=0
for pat in "${MANIFEST[@]}"; do
  for src in $pat; do
    n=$(basename "$src"); dst="$O/$n"
    case $mode in
      --check) cmp -s "$src" "$dst" || { echo "difere: $n ($src)"; diff=$((diff + 1)); } ;;
      --restore) if [ -f "$B/$n" ]; then cp "$B/$n" "$dst"; else rm -f "$dst"; fi ;;
      install)
        # kratosMove*: arquivos nossos (motor D11), não do Crimson — não viram "original"
        if [ -f "$dst" ] && [ ! -f "$B/$n" ] && [[ "$OURS" != *" $n "* ]] && [[ "$n" != kratosMove* ]] && ! cmp -s "$dst" "$src"; then
          echo "sem backup de $n (original do Crimson?): copiando para $B" ; cp "$dst" "$B/$n"; (cd "$B" && sha256sum "$n" >> SHA256SUMS)
        fi
        cp "$src" "$dst" ;;
    esac
  done
done
# tabela do motor Kratos (D11), lida pela DLL
J="Devil May Cry HD Collection/Crimson/configs/KratosMoves.json"
case $mode in
  install) cp "$I/release/KratosMoves.json" "$J" ;;
  --check) cmp -s "$I/release/KratosMoves.json" "$J" || { echo "difere: KratosMoves.json"; diff=$((diff + 1)); } ;;
  --restore) rm -f "$J" ;;
esac
# efeitos das magias do GoW1 (KratosFx.cpp lê Crimson\kratos_fx\*.kfx)
FX="Devil May Cry HD Collection/Crimson/kratos_fx"
for f in "$I"/release/kratos_fx/*.kfx; do
  case $mode in
    --check) cmp -s "$f" "$FX/$(basename "$f")" || { echo "difere: $(basename "$f")"; diff=$((diff + 1)); } ;;
    --restore) rm -f "$FX/$(basename "$f")" ;;
    install) mkdir -p "$FX"; cp "$f" "$FX/" ;;
  esac
done
# config do modo Kratos: instala a recomendada (config/KratosConfig.default.json) se ainda não houver (T75)
CFG="Devil May Cry HD Collection/Crimson/configs/KratosConfig.json"
[ "$mode" = install ] && [ ! -f "$CFG" ] && cp config/KratosConfig.default.json "$CFG" && echo "KratosConfig.json instalado (padrão)"
[ "$mode" = --check ] && echo "$diff arquivo(s) diferente(s)"
true
