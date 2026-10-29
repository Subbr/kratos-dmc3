#!/usr/bin/env bash
# Aperta teclas e captura AO MESMO TEMPO (trilhas paralelas do controle virtual): tools/win/act.sh "<teclas>" <n> <ms> <nome>
# Gera work/shots/<nome>_full.png (quadro inteiro, 1 a cada 2 capturas). Exige virtualPad.
set -e
cd "$(dirname "$0")/../.."
P="$(wslpath -w tools/win/game.ps1)"
powershell.exe -ExecutionPolicy Bypass -File "$P" keys "$1" >/dev/null &
tools/win/burst.sh "" "$2" "$3" "$4" >/dev/null
wait
tools/.venv/bin/python -I - "$4" <<'PY'
import glob, sys
from PIL import Image
fs = sorted(glob.glob(f"work/shots/burst/{sys.argv[1]}_*.png"))[::2]
ims = [Image.open(f).convert("RGB") for f in fs]
cw, ch, cols = 480, 270, 4
s = Image.new("RGB", (cw * cols, ch * ((len(ims) + cols - 1) // cols)))
for i, im in enumerate(ims):
    s.paste(im.resize((cw, ch)), ((i % cols) * cw, (i // cols) * ch))
s.save(f"work/shots/{sys.argv[1]}_full.png")
print(f"work/shots/{sys.argv[1]}_full.png")
PY
