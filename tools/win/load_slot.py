"""Diz qual slot está destacado na tela LOAD do DMC3 (o número fica branco): python -I load_slot.py <png>"""
import sys
import numpy as np
from PIL import Image

XS = (0.1875, 0.258, 0.325, 0.39, 0.458, 0.528, 0.597, 0.664, 0.731, 0.805)  # centro de cada número, 1..10
im = np.array(Image.open(sys.argv[1]).convert("RGB"), float)
h, w, _ = im.shape
white = (im[int(h * .17):int(h * .24)].min(axis=2) > 170).sum(axis=0)
score = [white[int((x - .025) * w):int((x + .025) * w)].sum() for x in XS]
print(int(np.argmax(score)) + 1 if max(score) > 200 else 0)
