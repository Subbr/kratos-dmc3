#!/usr/bin/env bash
# Instala o Crimson.dll do fork (dll/crimson) na pasta do jogo, com backup do original na primeira vez.
# Uso: tools/win/install_crimson_dll.sh [restore]
set -e
cd "$(dirname "$0")/../.."
GAME="Devil May Cry HD Collection"
BK=work/backup/crimson_override/Crimson.dll.release-0.5a
[ -f "$BK" ] || cp "$GAME/Crimson.dll" "$BK"
if [ "$1" = restore ]; then cp "$BK" "$GAME/Crimson.dll"; echo "restaurado o Crimson.dll original"; exit; fi
cp dll/crimson/build/bin/Release/Crimson.dll "$GAME/Crimson.dll"
sha256sum "$GAME/Crimson.dll" "$BK" | cut -c1-16
