"""Converte uma arma do GoW1 (glb estático do god_of_war_browser) num PAC de arma do DMC3 (ex.: plwp_sword.pac).

Uso: python -I tools/weapon_fit.py <arma.glb> <pasta do PAC base desempacotado> <saida.pac> [--scale 4.8]
Todos os vértices vão para um osso da arma (--bone; 1 na Rebellion, 1 ou 2 na Agni & Rudra). A arma é girada 180° em Y
(a lâmina do GoW1 aponta para −Z e a do DMC3 para +Z, com o cabo na origem) e 90° no eixo da lâmina
(--spin), para a face larga ficar no mesmo plano da Rebellion.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
import pac  # noqa: E402
import tex  # noqa: E402
from gltf import Glb  # noqa: E402
from kratos_fit import ROT_Y180, add_triangles, make_object, split, textures_block  # noqa: E402

def rot_z(deg: float) -> np.ndarray:
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def build_groups(g: Glb, scale: float, skip: set[str], spin: float = 0.0, bone: int = 1) -> dict[int, dict]:
    rot = rot_z(spin) @ ROT_Y180
    groups: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    tex_of_material = {i: m.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index", 0)
                       for i, m in enumerate(g.j["materials"])}
    for ni, nd in enumerate(g.j["nodes"]):
        if "mesh" not in nd:
            continue
        for p in g.j["meshes"][nd["mesh"]]["primitives"]:
            if g.j["materials"][p["material"]]["name"] in skip:
                continue
            a = p["attributes"]
            P = scale * (g.accessor(a["POSITION"]).astype(np.float64) @ rot.T)
            N = g.accessor(a["NORMAL"]).astype(np.float64) @ rot.T
            uv = g.accessor(a["TEXCOORD_0"])
            idx = g.accessor(p["indices"]).reshape(-1, 3) if "indices" in p else np.arange(len(P)).reshape(-1, 3)
            B = [bytes([0, 4 * bone, 0, 0])] * len(P)
            Q = [31] * len(P)
            add_triangles(groups[tex_of_material[p["material"]]], idx, P, N, uv, B, Q)
    return groups


def main(glb: Path, base_dir: Path, out_pac: Path, scale: float, skip: set[str], spin: float = 0.0,
         bone: int = 1, max_verts: int = 900) -> None:
    g = Glb(glb)
    model = mod.Model.parse((base_dir / "001.MOD").read_bytes())
    groups = build_groups(g, scale, skip, spin, bone)
    block = tex.TextureBlock.parse((base_dir / "000._").read_bytes())
    n_tex = len(block.textures)
    template = model.objects[0]
    model.objects = [make_object(template, t if t < n_tex else 0, part)
                     for t in sorted(groups) for part in split(groups[t], max_verts)]
    model.gaps = []
    model.tail = model.runtime_tail()
    model.auto_index_ptr = True
    work = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(base_dir, work / "pac", dirs_exist_ok=True)
        (work / "pac" / "001.MOD").write_bytes(model.build())
        (work / "pac" / "000._").write_bytes(textures_block(g, block))
        out_pac.parent.mkdir(parents=True, exist_ok=True)
        pac.repack(work / "pac", out_pac)
    finally:
        shutil.rmtree(work)
    pts = np.array([v for t in groups for v in groups[t]["pos"]])
    print(f"{out_pac}: {out_pac.stat().st_size} bytes; {len(model.objects)} objetos; "
          f"bbox {np.round(pts.min(0), 1)} {np.round(pts.max(0), 1)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("glb", type=Path)
    ap.add_argument("base", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--scale", type=float, default=4.8)
    ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--spin", type=float, default=90.0, help="giro em torno do eixo da lâmina (graus)")
    ap.add_argument("--bone", type=int, default=1, help="osso da arma (Rebellion: 1; Agni & Rudra: 1 ou 2, um por mão)")
    a = ap.parse_args()
    main(a.glb, a.base, a.out, a.scale, set(a.skip), a.spin, a.bone)
