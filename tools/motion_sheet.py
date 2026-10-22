"""Folha de quadros de motions do DMC3 posando a malha de um pl000 (para identificar o que cada motion é).

Uso: python -I tools/motion_sheet.py <pl000_00_N.pac> <índices, ex. 1,2,6> <saida.png> [--model pl000.pac] [--cols 6]
     python -I tools/motion_sheet.py --gow <nomes do GoW1, ex. combo3A,dash> <saida.png>
Frente (x, y) com o personagem olhando para a câmera; o osso 9 (mão direita) em vermelho.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_retarget as ar  # noqa: E402
import kratos_fit  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def pose(mo: mot.Motion, f: float, order, parent, off):
    W, P = {}, {}
    for b in order:
        r = ar.rot_xyz(*[mo.track(b, "r" + c).sample(f) if mo.track(b, "r" + c) else 0.0 for c in "xyz"])
        tt = [mo.track(b, "t" + c) for c in "xyz"]
        t = np.array([q.sample(f) if q else off[b][k] for k, q in enumerate(tt)]) if any(tt) else off[b]
        p = parent[b]
        W[b], P[b] = (r, t) if p < 0 else (W[p] @ r, P[p] + W[p] @ t)
    return W, P


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("which")
    ap.add_argument("out", type=Path)
    ap.add_argument("--gow", action="store_true", help="src = nomes de animações do GoW1 (retarget na hora)")
    ap.add_argument("--model", type=Path, default=ROOT / "work/install/kratos_v5/pl000.pac")
    ap.add_argument("--cols", type=int, default=6)
    a = ap.parse_args()
    dante = mod.Model.parse((ROOT / "extracted/dmc3/unpacked/pl000/001.MOD").read_bytes())
    body = mod.Model.parse(pac.Pac.parse(a.model.read_bytes()).entries[1])
    skel = body if body.bone_count > dante.bone_count else dante  # modelo com ossos de lâmina: usa o dele
    dj, parent = kratos_fit.dante_joints(skel)
    s = skel.skeleton
    order = [s.order[i] for i in range(len(parent))]
    off = [np.array(struct.unpack_from("<3f", t)) for t in s.transforms]
    pts = [(np.array(v), bi, w) for o in body.objects for m in o.meshes for v, bi, w in zip(m.positions, m.bones, m.weights)][::5]
    rows: list[tuple[str, mot.Motion]] = []
    if a.gow:
        g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
        cfg = yaml.safe_load((ROOT / "mapping/skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
        base = mot.Motion.parse(pac.Pac.parse((ROOT / "work/backup/crimson_override/pl000_00_0.pac").read_bytes()).entries[0])
        for name in a.src.split(","):
            n = max(int(ar.KratosAnim(g, name).duration * 60), 2)
            rows.append((f"{name} {n}f", ar.retarget(g, name, dante, cfg, n, base)))
    else:
        p = pac.Pac.parse(Path(a.src).read_bytes())
        for i in (int(x) for x in a.which.split(",")):
            m = mot.Motion.parse(p.entries[i])
            rows.append((f"#{i} {int(m.frames)}f", m))
    cw, ch = 120, 170
    img = Image.new("RGB", (a.cols * cw, len(rows) * ch), "white")
    d = ImageDraw.Draw(img)
    for r, (label, mo) in enumerate(rows):
        for c in range(a.cols):
            f = mo.frames * c / (a.cols - 1)
            W, P = pose(mo, f, order, parent, off)
            ox, oy = c * cw + cw // 2, r * ch + ch - 8
            root = P[0]
            for v, bi, w in pts:
                acc = np.zeros(3)
                for k in range(3):
                    ww = (w >> (5 * k)) & 31
                    if ww:
                        b = bi[1 + k] // 4
                        acc += ww / 31 * (W[b] @ (v - dj[b]) + P[b])
                acc[[0, 2]] -= root[[0, 2]]  # tira o deslocamento do golpe para caber no quadro
                d.point((ox + acc[0] * 0.5, oy - acc[1] * 0.5), fill=(200, 0, 0) if bi[1] // 4 in (9, 24, 25) else (0, 0, 0))
        d.text((2, r * ch + 2), label, fill="blue")
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
