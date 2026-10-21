"""Ajusta a malha do Kratos (glb do god_of_war_browser) ao esqueleto do Dante e gera um pl000.pac.

Uso: python -I tools/kratos_fit.py <kratos.glb> <pasta do pl000 desempacotado (base)> <saida.pac>
Mapeamento em mapping/skeleton_kratos_dante.yaml. Base esperada: pl000.pac do Crimson desempacotado.
"""
from __future__ import annotations

import io
import shutil
import struct
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
import pac  # noqa: E402
import tex  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROT_Y180 = np.diag([-1.0, 1.0, -1.0])


def dante_joints(model: mod.Model) -> tuple[np.ndarray, list[int]]:
    s = model.skeleton
    n = model.bone_count
    parent = [-1] * n
    for i in range(n):
        p = s.parents[i]
        parent[s.order[i]] = -1 if p == 255 else p
    local = [np.array(struct.unpack_from("<3f", t, 0)) for t in s.transforms]
    world = [None] * n

    def w(i):
        if world[i] is None:
            world[i] = local[i] + (w(parent[i]) if parent[i] >= 0 and parent[i] != i else 0)
        return world[i]

    return np.array([w(i) for i in range(n)]), parent


def rotation_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    v, c = np.cross(a, b), float(np.dot(a, b))
    if c < -0.999999:
        axis = np.cross(a, [1, 0, 0])
        axis = axis if np.linalg.norm(axis) > 1e-6 else np.cross(a, [0, 1, 0])
        axis /= np.linalg.norm(axis)
        return 2 * np.outer(axis, axis) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)


def fit_transforms(g: Glb, cfg: dict, dj: np.ndarray) -> tuple[list[np.ndarray], list[int]]:
    """Matriz 4x4 por junta do skin (espaço de bind girado -> espaço do Dante) e osso do Dante que recebe o peso."""
    skin = g.j["skins"][0]
    joints = skin["joints"]
    names = [g.name(i) for i in joints]
    ibm = g.accessor(skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    bind = {names[k]: ROT_Y180 @ np.linalg.inv(ibm[k])[:3, 3] for k in range(len(joints))}
    s = float(cfg["scale"])
    bones = cfg["bones"]
    by_name = {}
    for name, (dbone, kchild, dchild) in bones.items():
        m = s * np.eye(3)
        if kchild:
            dk = bind[kchild] - bind[name]
            dd = (dj[dchild] - dj[dbone]) if dchild is not None else None
            if dd is None:  # mão: gira como o antebraço do Dante, sem esticar
                par = next(n for n, v in bones.items() if v[1] == name)
                dd = dj[bones[name][0]] - dj[bones[par][0]]
                stretch = 1.0
            else:
                stretch = np.linalg.norm(dd) / (s * np.linalg.norm(dk))
            u = dk / np.linalg.norm(dk)
            m = rotation_between(dk, dd) @ (s * (np.eye(3) + (stretch - 1) * np.outer(u, u)))
        t = np.eye(4)
        t[:3, :3] = m
        t[:3, 3] = dj[dbone] - m @ bind[name]
        by_name[name] = (t, cfg.get("weights_target", {}).get(name, dbone))
    # ossos não mapeados herdam do ancestral mapeado mais próximo
    out_t, out_b = [], []
    for k, node in enumerate(joints):
        i = node
        while g.name(i) not in by_name:
            i = g.parent[i]
        t, b = by_name[g.name(i)]
        out_t.append(t)
        out_b.append(b)
    return out_t, out_b


def quantize3(weights: dict[int, float]) -> tuple[list[int], list[int]]:
    top = sorted(weights.items(), key=lambda kv: -kv[1])[:3]
    total = sum(w for _, w in top) or 1.0
    q = [int(round(31 * w / total)) for _, w in top]
    q[0] += 31 - sum(q)
    bones = [b for b, _ in top]
    while len(bones) < 3:
        bones.append(bones[0])
        q.append(0)
    return bones, q


def build_meshes(g: Glb, cfg: dict, dj: np.ndarray) -> dict[int, dict]:
    T, target = fit_transforms(g, cfg, dj)
    groups: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    for ni, nd in enumerate(g.j["nodes"]):
        if "mesh" not in nd:
            continue
        for p in g.j["meshes"][nd["mesh"]]["primitives"]:
            mat = g.j["materials"][p["material"]]["name"]
            if mat in cfg["skip_materials"]:
                continue
            a = p["attributes"]
            pos = g.accessor(a["POSITION"]).astype(np.float64) @ ROT_Y180.T
            nrm = g.accessor(a["NORMAL"]).astype(np.float64) @ ROT_Y180.T
            uv = g.accessor(a["TEXCOORD_0"])
            jnt = g.accessor(a["JOINTS_0"])
            wgt = g.accessor(a["WEIGHTS_0"])
            idx = g.accessor(p["indices"]).reshape(-1, 3) if "indices" in p else np.arange(len(pos)).reshape(-1, 3)
            P, N, B, Q = [], [], [], []
            for v in range(len(pos)):
                acc_p, acc_n, dw = np.zeros(3), np.zeros(3), defaultdict(float)
                for jk, wk in zip(jnt[v], wgt[v]):
                    if wk <= 0:
                        continue
                    t = T[int(jk)]
                    acc_p += wk * (t[:3, :3] @ pos[v] + t[:3, 3])
                    acc_n += wk * (np.linalg.inv(t[:3, :3]).T @ nrm[v])
                    dw[target[int(jk)]] += float(wk)
                P.append(acc_p)
                N.append(acc_n / (np.linalg.norm(acc_n) or 1))
                bones, q = quantize3(dw)
                B.append(bytes([0] + [4 * b for b in bones]))
                Q.append(q[0] | q[1] << 5 | q[2] << 10)
            grp = groups[cfg["textures"][mat]]
            for tri in idx:
                a0, b0, c0 = (int(x) for x in tri)
                # mantém a orientação majoritária do Dante: triângulo na posição par da strip, CCW em relação às normais
                fn = np.cross(P[b0] - P[a0], P[c0] - P[a0])
                if np.dot(fn, N[a0] + N[b0] + N[c0]) < 0:
                    b0, c0 = c0, b0
                for k, v in enumerate((a0, b0, c0)):
                    grp["pos"].append(tuple(P[v]))
                    grp["nrm"].append(tuple(N[v]))
                    u, w = float(uv[v][0]), float(uv[v][1])
                    grp["uv"].append((int(np.clip(round(u * 4096), -32768, 32767)), int(np.clip(round(w * 4096), -32768, 32767))))
                    grp["bones"].append(B[v])
                    grp["w"].append(Q[v] | (0x8000 if k < 2 else 0))
    return groups


def make_object(template: mod.Object, tex_idx: int, d: dict) -> mod.Object:
    pts = np.array(d["pos"])
    center = (pts.min(0) + pts.max(0)) / 2
    radius = float(np.linalg.norm(pts - center, axis=1).max())
    mesh = mod.Mesh(tex_idx, bytes(12), (0, 0, 0), d["pos"], d["nrm"], d["uv"], d["bones"], d["w"])
    return mod.Object(template.ukn, bytes(4), 0, bytes(28), (*center, radius), [mesh])


def textures_block(g: Glb, template_block: tex.TextureBlock) -> bytes:
    made = []
    for im in g.j["images"]:
        bv = g.j["bufferViews"][im["bufferView"]]
        data = g.bin[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
        buf = io.BytesIO()
        Image.open(io.BytesIO(data)).convert("RGBA").save(buf, format="DDS", pixel_format="DXT5")
        made.append(tex.make_texture(buf.getvalue(), template_block.textures[0].descriptor))
    while len(made) < len(template_block.textures):  # mantém a contagem de texturas da base
        made.append(made[0])
    return tex.TextureBlock(made).build()


def main(glb: Path, base_dir: Path, out_pac: Path) -> None:
    cfg = yaml.safe_load((ROOT / "mapping" / "skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
    g = Glb(glb)
    body = mod.Model.parse((base_dir / "001.MOD").read_bytes())
    dj, _ = dante_joints(body)
    groups = build_meshes(g, cfg, dj)
    template = body.objects[0]
    body.objects = [make_object(template, t, groups[t]) for t in sorted(groups)]
    body.gaps = []
    body.tail = b""
    coat = mod.Model.parse((base_dir / "012.MOD").read_bytes())
    for o in coat.objects:  # casaco do Dante: colapsa num ponto (some sem mexer na física de tecido)
        for m in o.meshes:
            m.positions = [(0.0, 116.0, 0.0)] * m.vert_count
    work = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(base_dir, work / "pac", dirs_exist_ok=True)
        (work / "pac" / "001.MOD").write_bytes(body.build())
        (work / "pac" / "012.MOD").write_bytes(coat.build())
        block = tex.TextureBlock.parse((base_dir / "000._").read_bytes())
        (work / "pac" / "000._").write_bytes(textures_block(g, block))
        out_pac.parent.mkdir(parents=True, exist_ok=True)
        pac.repack(work / "pac", out_pac)
    finally:
        shutil.rmtree(work)
    print(f"{out_pac}: {out_pac.stat().st_size} bytes; objetos {[(t, len(groups[t]['pos'])) for t in sorted(groups)]}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
