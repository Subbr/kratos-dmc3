"""Converte os modelos das magias do GoW1 (glb do god_of_war_browser) para o formato .kfx da DLL (KratosFx.cpp).

Uso: python -I tools/build_fx.py <pasta dos glb> <pasta de saída>   (tabela em mapping/magic_fx.yaml)
Formato .kfx (little endian): "KFX2", u32 n_sub; por sub: i32 textura, u32 mistura (0 opaca, 1 soma, 2 subtrai,
3 alfa), f32 cor[4], f32 ganho, u32 n_vért, u32 n_índ, vértices (pos f32×3, uv f32×2, cor f32×4), índices u32; u32 n_tex; por
textura: u32 tamanho + PNG. Posições em unidades do DMC3: × escala do esqueleto (4,8) e giro de 180° em Y.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kratos_fit  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BLENDS = {"opaque": 0, "add": 1, "sub": 2, "alpha": 3}


def node_world(g: Glb, node: int) -> np.ndarray:
    m = np.eye(4)
    n = g.j["nodes"][node]
    if "matrix" in n:
        m = np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T
    else:
        t = np.eye(4)
        t[:3, 3] = n.get("translation", [0, 0, 0])[:3]
        s = np.diag(list(n.get("scale", [1, 1, 1]))[:3] + [1])
        m = t @ s
    p = g.parent.get(node)
    return node_world(g, p) @ m if p is not None else m


def convert(glb: Path, out: Path, blend_conf: dict, gains: dict, scale: float) -> str:
    g = Glb(glb)
    j = g.j
    subs = []
    for ni, node in enumerate(j["nodes"]):
        if "mesh" not in node:
            continue
        w = node_world(g, ni)
        for prim in j["meshes"][node["mesh"]]["primitives"]:
            a = prim["attributes"]
            pos = g.accessor(a["POSITION"]).astype(np.float64)[:, :3]
            pos = (w @ np.c_[pos, np.ones(len(pos))].T).T[:, :3] * scale @ kratos_fit.ROT_Y180[:3, :3].T
            uv = g.accessor(a["TEXCOORD_0"]).astype(np.float64) if "TEXCOORD_0" in a else np.zeros((len(pos), 2))
            col = g.accessor(a["COLOR_0"]).astype(np.float64) if "COLOR_0" in a else np.ones((len(pos), 4))
            if col.shape[1] == 3:
                col = np.c_[col, np.ones(len(col))]
            idx = g.accessor(prim["indices"]).astype(np.uint32) if "indices" in prim else np.arange(len(pos), dtype=np.uint32)
            mat = j["materials"][prim["material"]] if "material" in prim else {}
            pbr = mat.get("pbrMetallicRoughness", {})
            tex = pbr.get("baseColorTexture", {}).get("index", -1)
            tex = j["textures"][tex]["source"] if tex >= 0 else -1
            name = mat.get("name", "")
            blend = blend_conf.get(name, blend_conf.get("default", "add"))
            # PS2: 0x80 = 1,0 → cor de vértice × 2 e, quando o material tem cor, × 2 de novo (T90: cabeça da Medusa com
            # vértice 0,502 = branco; raio com vértice 0,22 e material 0,3)
            gain = 2.0 * (2.0 if "baseColorFactor" in pbr else 1.0) * float(gains.get(name, 1.0))
            subs.append((tex, BLENDS[blend], pbr.get("baseColorFactor", [1, 1, 1, 1]), gain, pos, uv, col, idx))
    b = bytearray(b"KFX2") + struct.pack("<I", len(subs))
    for tex, blend, color, gain, pos, uv, col, idx in subs:
        b += struct.pack("<iI4ffII", tex, blend, *color, gain, len(pos), len(idx))
        b += np.c_[pos, uv, col].astype("<f4").tobytes() + idx.astype("<u4").tobytes()
    images = j.get("images", [])
    b += struct.pack("<I", len(images))
    for im in images:
        data = g.buffer_view(im["bufferView"])
        b += struct.pack("<I", len(data)) + bytes(data)
    out.write_bytes(b)
    return f"{out.name}: {len(subs)} partes, {sum(len(s[4]) for s in subs)} vértices, {len(images)} texturas"


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    conf = yaml.safe_load((ROOT / "mapping/magic_fx.yaml").read_text(encoding="utf-8"))
    scale = float(yaml.safe_load((ROOT / "mapping/skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))["scale"])
    dst.mkdir(parents=True, exist_ok=True)
    for name in conf["models"]:
        print(convert(src / f"{name}.glb", dst / f"{name}.kfx", conf["blend"], conf.get("gain", {}), scale))


if __name__ == "__main__":
    main()
