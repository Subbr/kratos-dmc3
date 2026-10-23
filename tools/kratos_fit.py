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
# lâmina do GoW1: comprimento no Z local, fio no Y; 180° no Z vira o fio sem mover o cabo (T17: fio para cima)
ROT_Z180 = np.diag([-1.0, -1.0, 1.0])


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


def build_meshes(g: Glb, cfg: dict, dj: np.ndarray) -> tuple[dict[int, dict], list[np.ndarray], list[int]]:
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
            add_triangles(groups[cfg["textures"][mat]], idx, P, N, uv, B, Q)
    return groups, T, target


def add_held_weapon(groups: dict, g: Glb, T: list[np.ndarray], target: list[int], weapon: Glb,
                    joint_name: str, tex_idx: int, bone_override: int | None = None,
                    flip_edge: bool = False) -> np.ndarray:
    """Prende uma arma (glb estático) ao osso de arma do Kratos (ex.: lWeapIH): pose do osso no GoW1 →
    mesmo ajuste do osso → peso total no osso do Dante correspondente."""
    joints = g.j["skins"][0]["joints"]
    k = next(i for i, n in enumerate(joints) if g.name(n) == joint_name)
    w = g.world(joints[k])
    t = T[k]
    lin = t[:3, :3] @ ROT_Y180 @ w[:3, :3] @ (ROT_Z180 if flip_edge else np.eye(3))
    off = t[:3, :3] @ (ROT_Y180 @ w[:3, 3]) + t[:3, 3]
    bone = bytes([0, 4 * (target[k] if bone_override is None else bone_override), 0, 0])
    for nd in weapon.j["nodes"]:
        if "mesh" not in nd:
            continue
        for p in weapon.j["meshes"][nd["mesh"]]["primitives"]:
            a = p["attributes"]
            P = weapon.accessor(a["POSITION"]).astype(np.float64) @ lin.T + off
            N = weapon.accessor(a["NORMAL"]).astype(np.float64) @ np.linalg.inv(lin)
            N /= np.linalg.norm(N, axis=1, keepdims=True).clip(1e-9)
            idx = weapon.accessor(p["indices"]).reshape(-1, 3) if "indices" in p else np.arange(len(P)).reshape(-1, 3)
            add_triangles(groups[tex_idx], idx, P, N, weapon.accessor(a["TEXCOORD_0"]), [bone] * len(P), [31] * len(P))
    return off  # posição do encaixe (osso de arma do Kratos) no espaço do Dante


# O ator do jogador só tem nós para 24 ossos por modelo (FUN_1401ef040 / FUN_14030f850, T15): as lâminas
# reaproveitam ossos do Dante. 23 (ponta da cabeça, sem vértices) = lâmina direita, filho da mão 9;
# 4 (pescoço) = lâmina esquerda, filho da mão 13; a cabeça (5) passa a ser filha do peito (3).
BLADE_BONES = {"rWeapIH": (23, 9), "lWeapIH": (4, 13)}  # osso reaproveitado -> pai (mão do Dante)
NECK, HEAD, CHEST = 4, 5, 3


def blade_cfg(cfg: dict) -> dict:
    """Mapeamento Kratos -> Dante sem o pescoço: vertebrae4 aponta para a cabeça; o pescoço herda (peito)."""
    out = {**cfg, "bones": {k: list(v) for k, v in cfg["bones"].items() if k != "neck"}}
    out["bones"]["vertebrae4"] = [CHEST, "head", HEAD]
    return out


def repurpose_blade_bones(model: mod.Model, grips: dict[str, np.ndarray], dj: np.ndarray) -> None:
    """Reaproveita os ossos 23 e 4 para as lâminas (ver BLADE_BONES) e refaz a hierarquia.
    O 3º array do esqueleto marca a parte superior do corpo (1 no tronco e braços): os ossos mantêm o seu."""
    s = model.skeleton
    n = model.bone_count
    parent = {s.order[i]: s.parents[i] for i in range(n)}
    upper = {s.order[i]: s.children[i] for i in range(n)}
    offs = [np.array(struct.unpack_from("<3f", t)) for t in s.transforms]
    offs[HEAD] = offs[NECK] + offs[HEAD]  # repouso sem rotação: offsets somam
    parent[HEAD] = CHEST
    for name, (bone, hand) in BLADE_BONES.items():
        parent[bone] = hand
        offs[bone] = grips[name] - dj[hand]
    order, stack = [], [b for b in range(n) if parent[b] == 255]
    children = {b: [c for c in range(n) if parent[c] == b] for b in range(n)}
    while stack:  # pai sempre antes dos filhos, filhos em ordem crescente
        b = stack.pop(0)
        order.append(b)
        stack = children[b] + stack
    s.order = bytes(order)
    s.parents = bytes(parent[b] for b in order)
    s.children = bytes(upper[b] for b in order)
    s.transforms = [struct.pack("<4f", *o, float(np.linalg.norm(o))) + t[16:] for o, t in zip(offs, s.transforms)]


def add_chains(groups: dict, grips: dict[str, np.ndarray], dj: np.ndarray, weapon: Glb, tex_idx: int,
               segments: int = 12, radius: float = 0.8) -> None:
    """Corrente entre a mão e a lâmina: tubo de 4 lados; o vértice na fração t do caminho tem peso (1 − t) na
    mão e t no osso da lâmina, então estica quando a motion afasta a lâmina (alcance do GoW1).
    Cor única: o pixel mais escuro e pouco saturado da textura da lâmina."""
    im = weapon.j["images"][0]
    bv = weapon.j["bufferViews"][im["bufferView"]]
    px = np.asarray(Image.open(io.BytesIO(weapon.bin[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]))
                    .convert("RGB"), dtype=float)
    lum, sat = px.mean(axis=2), px.max(axis=2) - px.min(axis=2)
    score = np.where((lum > 25) & (sat < 30), lum, 1e9)
    y, x = np.unravel_index(np.argmin(score), score.shape)
    uv = (x + 0.5) / px.shape[1], (y + 0.5) / px.shape[0]
    for name, (bone, parent) in BLADE_BONES.items():
        if name not in grips:
            continue
        a, b = dj[parent], grips[name]
        axis = (b - a) / np.linalg.norm(b - a)
        u = np.cross(axis, [0.0, 1.0, 0.0])
        u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-6 else np.array([1.0, 0.0, 0.0])
        v = np.cross(axis, u)
        ring = [radius * (np.cos(k * np.pi / 2) * u + np.sin(k * np.pi / 2) * v) for k in range(4)]
        P, N, B, Q = [], [], [], []
        for i in range(segments + 1):
            t = i / segments
            w_bone = int(round(31 * t))
            for r in ring:
                P.append(a + t * (b - a) + r)
                N.append(r / radius)
                B.append(bytes([0, 4 * parent, 4 * bone, 0]))
                Q.append((31 - w_bone) | (w_bone << 5))
        idx = []
        for i in range(segments):
            for k in range(4):
                p0, p1 = i * 4 + k, i * 4 + (k + 1) % 4
                idx += [(p0, p1, p0 + 4), (p1, p1 + 4, p0 + 4)]
        add_triangles(groups[tex_idx], np.array(idx), P, N, [uv] * len(P), B, Q)


def add_blade_bones(model: mod.Model, grips: dict[str, np.ndarray], dj: np.ndarray) -> None:
    """Acrescenta ao esqueleto um osso por lâmina, filho da mão, na posição do encaixe.
    O 3º array do esqueleto marca a parte superior do corpo (1 no tronco e nos braços): os novos recebem 1."""
    s = model.skeleton
    for name, (bone, parent) in BLADE_BONES.items():
        if name not in grips:
            continue
        assert bone == model.bone_count, "ossos novos em sequência"
        off = grips[name] - dj[parent]
        s.parents += bytes([parent])
        s.order += bytes([bone])
        s.children += bytes([1])
        s.transforms.append(struct.pack("<4f", *off, float(np.linalg.norm(off))) + bytes(16))
        model.bone_count += 1


def add_triangles(grp: dict, idx, P, N, uv, B, Q) -> None:
    """Grava cada triângulo como uma strip de 3 vértices (os 2 primeiros com o bit de reinício)."""
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


def split(d: dict, max_verts: int) -> list[dict]:
    """Divide um grupo em pedaços de até max_verts vértices (múltiplo de 3: um triângulo por 3 vértices)."""
    step = max_verts - max_verts % 3
    n = len(d["pos"])
    return [{k: v[i:i + step] for k, v in d.items()} for i in range(0, n, step)]


def empty_object(template: mod.Object, at: np.ndarray) -> mod.Object:
    """Objeto com 3 vértices e nenhum triângulo (todos com o bit de reinício)."""
    d = {"pos": [tuple(at)] * 3, "nrm": [(0.0, 1.0, 0.0)] * 3, "uv": [(0, 0)] * 3,
         "bones": [bytes([0, 4, 0, 0])] * 3, "w": [0x8000 | 31] * 3}
    return make_object(template, 0, d)


def make_object(template: mod.Object, tex_idx: int, d: dict) -> mod.Object:
    pts = np.array(d["pos"])
    center = (pts.min(0) + pts.max(0)) / 2
    radius = float(np.linalg.norm(pts - center, axis=1).max())
    mesh = mod.Mesh(tex_idx, bytes(12), (0, 0, 0), d["pos"], d["nrm"], d["uv"], d["bones"], d["w"])
    return mod.Object(template.ukn, bytes(4), 0, bytes(28), (*center, radius), [mesh])


def textures_block(g: Glb, template_block: tex.TextureBlock, extra: list[Glb] = (),
                   tint: tuple[float, float, float, float] | None = None) -> bytes:
    """Texturas do glb (na ordem das imagens) + a primeira imagem de cada glb extra.

    tint = (r, g, b, força): mistura cada textura com essa cor (brilho do Rage of the Gods no modelo de DT)."""
    made = []
    sources = [(g, im) for im in g.j["images"]] + [(e, e.j["images"][0]) for e in extra]
    for src, im in sources:
        bv = src.j["bufferViews"][im["bufferView"]]
        data = src.bin[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
        buf = io.BytesIO()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        if tint:
            glow = Image.new("RGBA", img.size, (*(int(c * 255) for c in tint[:3]), 255))
            img = Image.merge("RGBA", (*Image.blend(img, glow, tint[3]).split()[:3], img.split()[3]))
        img.save(buf, format="DDS", pixel_format="DXT5")
        made.append(tex.make_texture(buf.getvalue(), template_block.textures[0].descriptor))
    while len(made) < len(template_block.textures):  # mantém a contagem de texturas da base
        made.append(made[0])
    return tex.TextureBlock(made).build()


def main(glb: Path, base_dir: Path, out_pac: Path, max_verts: int = 900,
         use_body: bool = True, use_textures: bool = True, collapse_coat: bool = True,
         left_weapon: Path | None = None, reserve: int | None = None, both_hands: bool = False,
         blade_bones: bool = False, flip_edge: bool = False, hide: tuple[str, ...] = ("012.MOD",),
         tint: tuple[float, float, float, float] | None = None) -> None:
    cfg = yaml.safe_load((ROOT / "mapping" / "skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
    if blade_bones:
        cfg = blade_cfg(cfg)
    g = Glb(glb)
    body = mod.Model.parse((base_dir / "001.MOD").read_bytes())
    dj, _ = dante_joints(body)
    reserve = len(body.objects) if reserve is None else reserve
    groups, T, target = build_meshes(g, cfg, dj)
    extra = []
    grips: dict[str, np.ndarray] = {}
    if left_weapon:  # lâmina da mão esquerda: vai no corpo, presa ao lWeapIH, com textura no slot seguinte
        weapon = Glb(left_weapon)
        grips["lWeapIH"] = add_held_weapon(groups, g, T, target, weapon, "lWeapIH", len(g.j["images"]),
                                           BLADE_BONES["lWeapIH"][0] if blade_bones else None, flip_edge)
        if both_hands:  # GoW1: as lâminas nunca vão para as costas; a da direita também fica no corpo
            grips["rWeapIH"] = add_held_weapon(groups, g, T, target, weapon, "rWeapIH", len(g.j["images"]),
                                               BLADE_BONES["rWeapIH"][0] if blade_bones else None, flip_edge)
        extra.append(weapon)
    template = body.objects[0]
    if blade_bones and left_weapon:
        add_chains(groups, grips, dj, weapon, len(g.j["images"]))
    body.objects = [make_object(template, t, part) for t in sorted(groups) for part in split(groups[t], max_verts)]
    # o jogo liga/desliga objetos do Dante pelo índice (ex.: camisa na Missão 1; a coxa direita no objeto 5
    # sumia): os índices do Dante viram objetos vazios e o Kratos começa depois deles
    body.objects = [empty_object(template, dj[1])] * reserve + body.objects
    body.gaps = []
    if blade_bones:
        repurpose_blade_bones(body, grips, dj)
    body.tail = body.runtime_tail()
    body.auto_index_ptr = True
    hidden = {}
    for name in filter(None, hide):  # casaco do Dante, asas do DT: nenhum vértice fecha triângulo (some sem mexer na física)
        hidden[name] = mod.Model.parse((base_dir / name).read_bytes())
        for o in hidden[name].objects:
            for m in o.meshes:
                m.weights = [w | 0x8000 for w in m.weights]
    work = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(base_dir, work / "pac", dirs_exist_ok=True)
        if use_body:
            (work / "pac" / "001.MOD").write_bytes(body.build())
        if collapse_coat:
            for name, model in hidden.items():
                (work / "pac" / name).write_bytes(model.build())
        if use_textures:
            block = tex.TextureBlock.parse((base_dir / "000._").read_bytes())
            (work / "pac" / "000._").write_bytes(textures_block(g, block, extra, tint))
        out_pac.parent.mkdir(parents=True, exist_ok=True)
        pac.repack(work / "pac", out_pac)
    finally:
        shutil.rmtree(work)
    print(f"{out_pac}: {out_pac.stat().st_size} bytes; {len(body.objects)} objetos; corpo={use_body} "
          f"texturas={use_textures} casaco_oculto={collapse_coat}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("glb", type=Path)
    ap.add_argument("base", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--max-verts", type=int, default=900)
    ap.add_argument("--no-body", action="store_true")
    ap.add_argument("--no-textures", action="store_true")
    ap.add_argument("--keep-coat", action="store_true")
    ap.add_argument("--left-weapon", type=Path, help="glb da arma presa à mão esquerda (lWeapIH)")
    ap.add_argument("--both-hands", action="store_true", help="com --left-weapon: a mesma arma também no rWeapIH")
    ap.add_argument("--blade-bones", action="store_true", help="lâminas nos ossos 23 (dir.) e 4 (esq.), reaproveitados")
    ap.add_argument("--flip-edge", action="store_true", help="gira as lâminas 180° no eixo do comprimento")
    ap.add_argument("--reserve", type=int, help="objetos vazios no início (padrão: quantos o Dante tem)")
    ap.add_argument("--hide", default="012.MOD", help="MODs da base a esconder, separados por vírgula (padrão: casaco)")
    ap.add_argument("--tint", help="r,g,b,força: cor misturada nas texturas (ex. DT: 1,0.75,0.2,0.35)")
    a = ap.parse_args()
    main(a.glb, a.base, a.out, a.max_verts, not a.no_body, not a.no_textures, not a.keep_coat, a.left_weapon, a.reserve, a.both_hands, a.blade_bones,
         a.flip_edge, tuple(a.hide.split(",")), tuple(map(float, a.tint.split(","))) if a.tint else None)
