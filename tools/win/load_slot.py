"""Lê a tela LOAD do DMC3: python -I load_slot.py <png> [slot|dialog]
slot: número destacado (branco), 0 se não achar. dialog: "yes", "no" ou "none" (OK to load this file?)."""
import sys
import numpy as np
from PIL import Image

XS = (0.1875, 0.258, 0.325, 0.39, 0.458, 0.528, 0.597, 0.664, 0.731, 0.805)  # centro de cada número, 1..10
im = np.array(Image.open(sys.argv[1]).convert("RGB"), float)
h, w, _ = im.shape
mode = sys.argv[2] if len(sys.argv) > 2 else "slot"
if mode == "slot":
    white = (im[int(h * .17):int(h * .24)].min(axis=2) > 170).sum(axis=0)
    score = [white[int((x - .025) * w):int((x + .025) * w)].sum() for x in XS]
    print(int(np.argmax(score)) + 1 if max(score) > 200 else 0)
else:
    gray = im.mean(axis=2)
    row = gray[int(h * .73):int(h * .78)]
    yes, no = row[:, int(w * .34):int(w * .40)].mean(), row[:, int(w * .41):int(w * .46)].mean()
    opts = (row[:, int(w * .33):int(w * .47)] > 150).mean()  # linha "Yes No" só existe no diálogo
    print("none" if opts < 0.01 else ("yes" if yes > no else "no"))
