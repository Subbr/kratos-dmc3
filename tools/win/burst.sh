#!/usr/bin/env bash
# Aperta teclas e captura N quadros; monta uma folha de contato: tools/win/burst.sh "<seq>" <n> <ms> <nome>
set -e
cd "$(dirname "$0")/../.."
W=$(wslpath -w "$PWD")   # raiz do projeto no Windows (sem caminho fixo)
mkdir -p work/shots/burst
rm -f work/shots/burst/$4_*.png
powershell.exe -ExecutionPolicy Bypass -File "$W\tools\win\game.ps1" burst "$1|$2|$3|$W\work\shots\burst\\$4" >/dev/null
tools/.venv/bin/python -I - "$4" <<'PY'
import sys, glob
from PIL import Image
fs = sorted(glob.glob(f"work/shots/burst/{sys.argv[1]}_*.png"))
ims = [Image.open(f).convert("RGB") for f in fs]
w, h = 400, ims[0].height * 400 // ims[0].width
cols = 4
sheet = Image.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)))
for i, im in enumerate(ims):
    # recorte central (o personagem fica no meio) ampliado
    W, H = im.size
    im = im.crop((W // 4, H // 6, W * 3 // 4, H * 5 // 6)).resize((w, h))
    sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(f"work/shots/{sys.argv[1]}_sheet.png")
print(f"work/shots/{sys.argv[1]}_sheet.png")
PY
