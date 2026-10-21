"""Folha ampliada de uma sequência: python -I tools/win/zoom.py <nome> <cx> <cy> <meia-largura> [saida]
cx, cy, meia-largura em fração da tela (ex.: 0.49 0.6 0.1)."""
import glob
import sys
from PIL import Image

name, cx, cy, hw = sys.argv[1], *map(float, sys.argv[2:5])
fs = sorted(glob.glob(f"work/shots/burst/{name}_*.png"))
cell = 300
cols = 6
sheet = Image.new("RGB", (cell * cols, int(cell * 1.3) * ((len(fs) + cols - 1) // cols)))
for i, f in enumerate(fs):
    im = Image.open(f).convert("RGB")
    W, H = im.size
    hh = hw * W * 1.3 / 2
    box = (int((cx - hw) * W), int(cy * H - hh), int((cx + hw) * W), int(cy * H + hh))
    sheet.paste(im.crop(box).resize((cell, int(cell * 1.3))), ((i % cols) * cell, (i // cols) * int(cell * 1.3)))
out = sys.argv[5] if len(sys.argv) > 5 else f"work/shots/{name}_zoom.png"
sheet.save(out)
print(out)
