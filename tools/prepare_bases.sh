#!/usr/bin/env bash
# Junta em work/backup/crimson_override os arquivos-base do DMC3/Crimson que o build do modo Kratos lê
# (lista e hashes esperados em config/bases.sha256). Fonte: o override do Crimson 0.5a recém-instalado
# (data/dmc3/GData.afs) ou, se não estiver lá, o dmc3-0.nbz do jogo. Rodar ANTES do primeiro tools/install_all.sh.
# Uso: tools/prepare_bases.sh
set -eu
cd "$(dirname "$0")/.."
source config/paths.env
O="$DMC_HD_DIR/data/dmc3/GData.afs"; B=work/backup/crimson_override
mkdir -p "$B"
ok=0; bad=0
while read -r sum name; do
  dst="$B/$name"
  [ -f "$dst" ] && [ "$(sha256sum < "$dst" | cut -c1-64)" = "$sum" ] && { ok=$((ok + 1)); continue; }
  if [ "$name" = Crimson.dll.release-0.5a ]; then src="$DMC_HD_DIR/Crimson.dll"; else src="$O/$name"; fi
  if [ -f "$src" ] && [ "$(sha256sum < "$src" | cut -c1-64)" = "$sum" ]; then
    cp "$src" "$dst"; ok=$((ok + 1)); continue
  fi
  if tools/.venv/bin/python -I -c 'import sys, zipfile; sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read(sys.argv[2]))' \
       "$DMC3_NBZ" "GData.afs/$name" > "$dst.tmp" 2>/dev/null && [ "$(sha256sum < "$dst.tmp" | cut -c1-64)" = "$sum" ]; then
    mv "$dst.tmp" "$dst"; ok=$((ok + 1)); continue
  fi
  rm -f "$dst.tmp"; echo "FALTA ou hash diferente: $name"; bad=$((bad + 1))
done < config/bases.sha256
echo "bases: $ok ok, $bad com problema"
[ "$bad" = 0 ] || { echo "Confira se o Crimson 0.5a está instalado e o override ainda não tem arquivos do Kratos."; exit 1; }
