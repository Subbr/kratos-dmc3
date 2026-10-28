"""Kratos do GoW1 para o renderizador da DLL (T98, KratosBody.cpp): esqueleto, malhas, texturas, lâminas e animações
originais, sem passar pelo esqueleto do Dante.

Uso: python -I tools/build_body.py <hero_obj.glb> <maiblade.glb> <saída.kbd> [--preview <animação> <tempo s> <png>]
Formato KBD1 (little-endian):
  u32 nós; por nó: i32 pai, f32 T[3] R[4] S[3], char nome[32]
  u32 juntas da pele; u32 nó[n]; f32 inversa do bind[n][16] (glTF coluna-major = linha-major de vetor-linha)
  u32 texturas; por textura: u32 tamanho, PNG
  u32 partes; por parte: i32 textura, i32 nó rígido (-1 = pele), u32 nv, ni;
      vértices nv × (f32 pos[3], nrm[3], uv[2], cor[4]; u16 juntas[4]; f32 pesos[4]); índices u32[ni]
  u32 animações; por animação: char nome[32], f32 duração, u32 canais; por canal: u32 nó, u32 caminho (0 T, 1 R, 2 S),
      u32 chaves, f32 tempos[k], f32 valores[k × 3|4]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf import Glb  # noqa: E402

PATHS = {"translation": 0, "rotation": 1, "scale": 2}
BLADE_NODES = {"rWeapIH": 0, "lWeapIH": 1}  # a lâmina vai presa à junta "na mão" (FUN_001fa8a8 do GoW1, estado 1)


def name32(s: str) -> bytes:
    b = s.encode("ascii", "replace")[:31]
    return b + b"\0" * (32 - len(b))


def node_parents(j: dict) -> list[int]:
    par = [-1] * len(j["nodes"])
    for i, n in enumerate(j["nodes"]):
        for c in n.get("children", []):
            par[c] = i
    return par


def prim_data(g: Glb, p: dict, rigid: bool):
    a = p["attributes"]
    pos = g.accessor(a["POSITION"]).astype(np.float32)
    n = len(pos)
    nrm = g.accessor(a["NORMAL"]).astype(np.float32) if "NORMAL" in a else np.zeros((n, 3), np.float32)
    uv = g.accessor(a["TEXCOORD_0"]).astype(np.float32) if "TEXCOORD_0" in a else np.zeros((n, 2), np.float32)
    col = g.accessor(a["COLOR_0"]).astype(np.float32) if "COLOR_0" in a else np.ones((n, 4), np.float32)
    if col.shape[1] == 3:
        col = np.hstack([col, np.ones((n, 1), np.float32)])
    if rigid or "JOINTS_0" not in a:
        jnt = np.zeros((n, 4), np.uint16)
        wgt = np.tile(np.array([1, 0, 0, 0], np.float32), (n, 1))
    else:
        jnt = g.accessor(a["JOINTS_0"]).astype(np.uint16)
        wgt = g.accessor(a["WEIGHTS_0"]).astype(np.float32)
    idx = g.accessor(p["indices"]).astype(np.uint32).ravel() if "indices" in p else np.arange(n, dtype=np.uint32)
    return pos, nrm, uv, col, jnt, wgt, idx


def write_prim(out: bytearray, tex: int, rigid_node: int, data) -> None:
    pos, nrm, uv, col, jnt, wgt, idx = data
    out += struct.pack("<iiII", tex, rigid_node, len(pos), len(idx))
    for k in range(len(pos)):
        out += struct.pack("<12f", *pos[k], *nrm[k], *uv[k], *col[k])
        out += struct.pack("<4H", *jnt[k])
        out += struct.pack("<4f", *wgt[k])
    out += idx.astype("<u4").tobytes()


def build(hero: Path, blade: Path, dst: Path) -> dict:
    g, b = Glb(hero), Glb(blade)
    j, bj = g.j, b.j
    out = bytearray(b"KBD1")
    par = node_parents(j)
    names = [n.get("name") or "" for n in j["nodes"]]
    out += struct.pack("<I", len(j["nodes"]))
    for i, n in enumerate(j["nodes"]):
        out += struct.pack("<i10f", par[i], *n.get("translation", [0, 0, 0]), *n.get("rotation", [0, 0, 0, 1]),
                           *n.get("scale", [1, 1, 1]))
        out += name32(names[i])
    skin = j["skins"][0]
    ibm = g.accessor(skin["inverseBindMatrices"]).astype(np.float32).reshape(-1, 16)
    out += struct.pack("<I", len(skin["joints"]))
    out += struct.pack(f"<{len(skin['joints'])}I", *skin["joints"])
    out += ibm.astype("<f4").tobytes()
    # texturas: as do herói e depois as da lâmina
    texs = []
    for gg in (g, b):
        for img in gg.j.get("images", []):
            texs.append(gg.buffer_view(img["bufferView"]))
    out += struct.pack("<I", len(texs))
    for t in texs:
        out += struct.pack("<I", len(t)) + t
    nhero = len(j.get("images", []))
    prims = []
    for m in j["meshes"]:
        for p in m["primitives"]:
            mat = j["materials"][p["material"]] if "material" in p else {}
            if mat.get("name") == "MAT_ClothCollisionMat":
                continue  # volume de colisão do saiote: não é desenhado no GoW1
            t = mat.get("pbrMetallicRoughness", {}).get("baseColorTexture")
            tex = j["textures"][t["index"]]["source"] if t else -1
            prims.append((tex, -1, prim_data(g, p, False)))
    # lâmina (Blade of Chaos): malha 0 do maiblade.glb na pose de bind, presa a r/lWeapIH
    bm = bj["meshes"][0]["primitives"][0]
    bmat = bj["materials"][bm["material"]] if "material" in bm else {}
    bt = bmat.get("pbrMetallicRoughness", {}).get("baseColorTexture")
    btex = nhero + bj["textures"][bt["index"]]["source"] if bt else -1
    bdata = prim_data(b, bm, True)
    for nm in BLADE_NODES:
        prims.append((btex, names.index(nm), bdata))
    out += struct.pack("<I", len(prims))
    for tex, rigid, data in prims:
        write_prim(out, tex, rigid, data)
    anims = j.get("animations", [])
    out += struct.pack("<I", len(anims))
    for a in anims:
        chans = []
        dur = 0.0
        for c in a["channels"]:
            s = a["samplers"][c["sampler"]]
            t = g.accessor(s["input"]).astype(np.float32).ravel()
            v = g.accessor(s["output"]).astype(np.float32).reshape(len(t), -1)
            v = v[:, :4] if c["target"]["path"] == "rotation" else v[:, :3]  # o gowb grava translação como vec4
            dur = max(dur, float(t[-1]) if len(t) else 0.0)
            chans.append((c["target"]["node"], PATHS[c["target"]["path"]], t, v))
        out += name32(a["name"].split(" ")[-1]) + struct.pack("<fI", dur, len(chans))
        for node, path, t, v in chans:
            out += struct.pack("<III", node, path, len(t)) + t.astype("<f4").tobytes() + v.astype("<f4").tobytes()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(bytes(out))
    return {"nodes": len(j["nodes"]), "skin": len(skin["joints"]), "textures": len(texs), "parts": len(prims),
            "anims": len(anims), "bytes": len(out)}


def quat_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def preview(hero: Path, blade: Path, anim: str, t: float, png: Path) -> None:
    """Prévia da pose (pele na CPU, mesmo cálculo da DLL) em PNG, de lado, pela cor por vértice."""
    import anim_retarget as ar
    from PIL import Image, ImageDraw
    g = Glb(hero)
    j = g.j
    par = node_parents(j)
    a = ar.KratosAnim(g, anim)
    world = [None] * len(j["nodes"])

    def w(i):
        if world[i] is None:
            n = j["nodes"][i]
            T = a._value(i, "translation", t, n.get("translation", [0, 0, 0]))[:3]
            R = a._value(i, "rotation", t, n.get("rotation", [0, 0, 0, 1]))[:4]
            S = a._value(i, "scale", t, n.get("scale", [1, 1, 1]))[:3]
            L = np.eye(4)
            L[:3, :3] = quat_mat(R) * np.array(S)
            L[:3, 3] = T
            world[i] = (w(par[i]) if par[i] >= 0 else np.eye(4)) @ L
        return world[i]

    skin = j["skins"][0]
    ibm = g.accessor(skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    pal = [w(nd) @ ibm[k] for k, nd in enumerate(skin["joints"])]
    img = Image.new("RGB", (600, 700), (40, 40, 48))
    d = ImageDraw.Draw(img)
    tris = []
    for m in j["meshes"]:
        for p in m["primitives"]:
            mat = j["materials"][p["material"]] if "material" in p else {}
            if mat.get("name") == "MAT_ClothCollisionMat":
                continue
            pos, nrm, uv, col, jnt, wgt, idx = prim_data(g, p, False)
            sk = np.zeros((len(pos), 3))
            for k in range(4):
                M = np.stack([pal[x] for x in jnt[:, k]])
                ph = np.einsum("nij,nj->ni", M, np.hstack([pos, np.ones((len(pos), 1))]))[:, :3]
                sk += ph * wgt[:, k:k + 1]
            for f in range(0, len(idx), 3):
                v = sk[idx[f:f + 3]]
                c = np.clip(col[idx[f]][:3] * 2 * 255, 0, 255).astype(int)
                tris.append((v[:, 2].mean(), v, tuple(c)))
    tris.sort(key=lambda x: x[0])
    for _, v, c in tris:
        d.polygon([(300 + p[0] * 6, 650 - p[1] * 6) for p in v], fill=c)
    img.save(png)


if __name__ == "__main__":
    info = build(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(info)
    if "--preview" in sys.argv:
        k = sys.argv.index("--preview")
        preview(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[k + 1], float(sys.argv[k + 2]), Path(sys.argv[k + 3]))
