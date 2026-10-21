"""Reduz uma captura de tela para inspeção: python -I tools/win/thumb.py <in.png> <out.png> [largura]"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]); w = int(sys.argv[3]) if len(sys.argv) > 3 else 960
im.convert("RGB").resize((w, im.height * w // im.width)).save(sys.argv[2])
