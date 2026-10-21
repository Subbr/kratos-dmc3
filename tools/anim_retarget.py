"""Retarget de uma animação do Kratos (glb do god_of_war_browser) para uma motion (MOT) do Dante.

Para cada osso do Dante com par no Kratos, a rotação de mundo é
    W_dante(t) = C · R_kratos(t) · C · F⁻¹
C = giro de 180° em Y; R_kratos = parte de rotação de mundo(t) · inverseBind; F = rotação que o
kratos_fit usou para levar o osso do Kratos ao do Dante. Assim cada osso do Dante aponta para onde o
osso do Kratos aponta, e a malha ajustada pelo kratos_fit se move como a do GoW1.
A rotação local (pai⁻¹ · filho) vira ângulos de Euler XYZ (R = Rz·Ry·Rx, convenção do importador
DMC3/motion.py, [INFERIDO]). O quadril (osso 1) recebe a translação da pelve do Kratos.

Uso: python -I tools/anim_retarget.py <kratos.glb> <animação> <pl000_00_N.pac base> <índice> <saida.pac>
         [--frames N]  (padrão: mantém a duração da motion original)  [--timing stretch|natural]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kratos_fit  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
C = kratos_fit.ROT_Y180
HIP, PELVIS_SRC = 1, "pelvis"
ROOT_MOTION_BONE = 0


def _quat_to_mat(q: np.ndarray) -> np.ndarray:
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def _slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    d = float(np.dot(a, b))
    if d < 0:
        b, d = -b, -d
    if d > 0.9995:
        r = a + t * (b - a)
        return r / np.linalg.norm(r)
    th = np.arccos(d)
    return (np.sin((1 - t) * th) * a + np.sin(t * th) * b) / np.sin(th)


def _polar_rotation(m: np.ndarray) -> np.ndarray:
    u, _, vt = np.linalg.svd(m)
    r = u @ vt
    if np.linalg.det(r) < 0:
        u[:, -1] *= -1
        r = u @ vt
    return r


def euler_xyz(r: np.ndarray) -> tuple[float, float, float]:
    """Inverso de R = Rz(z) · Ry(y) · Rx(x)."""
    y = np.arcsin(-np.clip(r[2, 0], -1, 1))
    if abs(r[2, 0]) < 0.99999:
        x = np.arctan2(r[2, 1], r[2, 2])
        z = np.arctan2(r[1, 0], r[0, 0])
    else:
        x, z = np.arctan2(-r[1, 2], r[1, 1]), 0.0
    return float(x), float(y), float(z)


def rot_xyz(x: float, y: float, z: float) -> np.ndarray:
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


class KratosAnim:
    """Amostra uma animação do glb em qualquer tempo (interpolação linear / slerp)."""

    def __init__(self, g: Glb, name: str):
        self.g = g
        # nomes do glb: "hero <nome>", alguns com outro prefixo (ex.: "hero lk berWalkBlend0")
        anim = next((a for a in g.j["animations"] if a["name"] in (name, f"hero {name}")), None) or \
            next((a for a in g.j["animations"] if a["name"].split()[-1] == name), None)
        if anim is None:
            raise KeyError(f"animação {name!r} não encontrada")
        self.channels = {}
        for c in anim["channels"]:
            s = anim["samplers"][c["sampler"]]
            self.channels[(c["target"]["node"], c["target"]["path"])] = (g.accessor(s["input"]), g.accessor(s["output"]))
        self.duration = max(float(t[-1]) for t, _ in self.channels.values())

    def _value(self, node: int, path: str, t: float, default):
        if (node, path) not in self.channels:
            return np.array(default, dtype=np.float64)
        times, vals = self.channels[(node, path)]
        vals = np.asarray(vals, dtype=np.float64)
        if t <= times[0] or len(times) == 1:
            return vals[0]
        if t >= times[-1]:
            return vals[-1]
        i = int(np.searchsorted(times, t)) - 1
        f = (t - times[i]) / (times[i + 1] - times[i])
        return _slerp(vals[i], vals[i + 1], f) if path == "rotation" else vals[i] + f * (vals[i + 1] - vals[i])

    def local(self, node: int, t: float) -> np.ndarray:
        n = self.g.j["nodes"][node]
        m = np.eye(4)
        r = self._value(node, "rotation", t, n.get("rotation", [0, 0, 0, 1]))
        m[:3, :3] = _quat_to_mat(r) * self._value(node, "scale", t, n.get("scale", [1, 1, 1]))
        m[:3, 3] = self._value(node, "translation", t, n.get("translation", [0, 0, 0]))[:3]  # glb do gowb: VEC4
        return m

    def world(self, node: int, t: float, cache: dict) -> np.ndarray:
        if node not in cache:
            p = self.g.parent.get(node)
            cache[node] = (self.world(p, t, cache) if p is not None else np.eye(4)) @ self.local(node, t)
        return cache[node]


def retarget(g: Glb, anim_name: str, body: mod.Model, cfg: dict, frames: int, base: mot.Motion,
             timing: str = "stretch") -> mot.Motion:
    """timing: "stretch" = a animação inteira ocupa os frames da motion base; "natural" = 60 fps do
    GoW1 (o glb tem tempo em segundos) e o último quadro fica parado até o fim da motion base.
    Tracks do osso 0 (deslocamento do personagem no golpe) vêm da motion base sem mudança."""
    dj, parent = kratos_fit.dante_joints(body)
    T, _ = kratos_fit.fit_transforms(g, cfg, dj)
    skin = g.j["skins"][0]
    joints = skin["joints"]
    names = [g.name(j) for j in joints]
    ibm = g.accessor(skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1).astype(np.float64)
    # osso do Dante -> junta do Kratos (primeira do yaml com direção; senão a primeira)
    src: dict[int, int] = {}
    for name, (dbone, kchild, _) in cfg["bones"].items():
        if name in names and (dbone not in src or (kchild and not cfg["bones"][names[src[dbone]]][1])):
            src[dbone] = names.index(name)
    F = {d: _polar_rotation(T[k][:3, :3]) for d, k in src.items()}
    anim = KratosAnim(g, anim_name)
    s = float(cfg["scale"])
    k_pelvis = names.index(PELVIS_SRC)
    pelvis_bind = C @ np.linalg.inv(ibm[k_pelvis])[:3, 3]

    n = len(parent)
    rot_tracks = [b for b in range(n) if any(t.bone == b and t.channel[0] == "r" for t in base.tracks)]
    values: dict[tuple[int, str], list[float]] = {}
    prev: dict[int, np.ndarray] = {}
    order = [body.skeleton.order[i] for i in range(n)]
    for f in range(frames):
        t = anim.duration * f / max(frames - 1, 1) if timing == "stretch" else min(f / 60.0, anim.duration)
        cache: dict = {}
        W = [np.eye(3)] * n
        for d in order:  # ordem do esqueleto: pai antes do filho
            if d in src:
                k = src[d]
                rk = _polar_rotation((anim.world(joints[k], t, cache) @ ibm[k])[:3, :3])
                W[d] = C @ rk @ C @ F[d].T
            else:
                W[d] = W[parent[d]] if parent[d] >= 0 else np.eye(3)
        for d in rot_tracks:
            pw = W[parent[d]] if parent[d] >= 0 else np.eye(3)
            e = np.array(euler_xyz(pw.T @ W[d]))
            if d in prev:  # continuidade: escolhe o equivalente mais próximo do frame anterior
                e = prev[d] + (e - prev[d] + np.pi) % (2 * np.pi) - np.pi
            prev[d] = e
            for c, v in zip("xyz", e):
                values.setdefault((d, "r" + c), []).append(float(v))
        hip = s * (C @ anim.world(joints[k_pelvis], t, cache)[:3, 3] - pelvis_bind) + dj[HIP]
        for c, v in zip("xyz", hip):
            values.setdefault((HIP, "t" + c), []).append(float(v))

    out = mot.Motion(bytearray(base.header))
    out.frames = float(frames - 1)  # o cabeçalho guarda o último frame (chaves de 0 a N)
    out.tracks = [mot.Track.hermite(b, ch, v) for (b, ch), v in values.items()]
    out.tracks += [t for t in base.tracks if t.bone == ROOT_MOTION_BONE]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("glb", type=Path)
    ap.add_argument("anim")
    ap.add_argument("base_pac", type=Path)
    ap.add_argument("index", type=int)
    ap.add_argument("out", type=Path)
    ap.add_argument("--body", type=Path, default=ROOT / "extracted/dmc3/unpacked/pl000/001.MOD")
    ap.add_argument("--frames", type=int)
    ap.add_argument("--timing", choices=("stretch", "natural"), default="stretch")
    a = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "mapping" / "skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
    g = Glb(a.glb)
    body = mod.Model.parse(a.body.read_bytes())
    p = pac.Pac.parse(a.base_pac.read_bytes())
    base = mot.Motion.parse(p.entries[a.index])
    frames = a.frames or int(round(base.frames)) + 1
    new = retarget(g, a.anim, body, cfg, frames, base, a.timing)
    p.entries[a.index] = new.build(pad=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(p.build())
    print(f"{a.out}: motion {a.index} = {a.anim} ({frames} frames, {len(new.tracks)} tracks)")


if __name__ == "__main__":
    main()
