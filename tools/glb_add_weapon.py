"""Junta uma arma do GoW1 (glb estático) ao glb do Kratos, presa aos ossos de arma (lWeapIH/rWeapIH), para os
renders das artes de menu (T77). Mesmo encaixe do kratos_fit.add_held_weapon, mas no espaço do glb: a malha da arma
vira primitivas novas com peso total no osso de arma, então segue qualquer pose de animação no Blender.

Uso: python -I tools/glb_add_weapon.py <kratos.glb> <arma.glb> <saída.glb> [--joints lWeapIH,rWeapIH] [--flip-edge]
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf import Glb  # noqa: E402

ROT_Z180 = np.diag([-1.0, -1.0, 1.0])


class Writer:
    """Acrescenta bufferViews/accessors ao fim do binário do glb base."""

    def __init__(self, g: Glb):
        self.j = json.loads(json.dumps(g.j))
        self.bin = bytearray(g.bin[: self.j["buffers"][0]["byteLength"]])

    def view(self, data: bytes, target: int | None = None) -> int:
        self.bin += b"\0" * (-len(self.bin) % 4)
        bv = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(data)}
        if target:
            bv["target"] = target
        self.bin += data
        self.j["bufferViews"].append(bv)
        return len(self.j["bufferViews"]) - 1

    def accessor(self, arr: np.ndarray, kind: str, comp: int, target: int | None = None) -> int:
        acc = {"bufferView": self.view(arr.tobytes(), target), "componentType": comp, "count": len(arr), "type": kind}
        if kind == "VEC3" and comp == 5126:
            acc["min"], acc["max"] = arr.min(0).tolist(), arr.max(0).tolist()
        self.j["accessors"].append(acc)
        return len(self.j["accessors"]) - 1

    def save(self, out: Path) -> None:
        self.j["buffers"][0]["byteLength"] = len(self.bin)
        js = json.dumps(self.j, separators=(",", ":")).encode()
        js += b" " * (-len(js) % 4)
        self.bin += b"\0" * (-len(self.bin) % 4)
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        out.write_bytes(struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<I4s", len(js), b"JSON") + js
                        + struct.pack("<I4s", len(self.bin), b"BIN\0") + bytes(self.bin))


def add_weapon(g: Glb, weapon: Glb, joints: list[str], flip_edge: bool) -> Writer:
    w = Writer(g)
    skin = w.j["skins"][0]["joints"]
    # material da arma: a imagem vem do binário da arma
    mat_of: dict[int, int] = {}
    for mi, m in enumerate(weapon.j["materials"]):
        t = weapon.j["textures"][m["pbrMetallicRoughness"]["baseColorTexture"]["index"]]
        img = weapon.j["images"][t["source"]]
        bv = weapon.j["bufferViews"][img["bufferView"]]
        data = weapon.bin[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
        w.j["images"].append({"name": img["name"], "mimeType": img["mimeType"], "bufferView": w.view(data)})
        w.j["samplers"].append(weapon.j["samplers"][t.get("sampler", 0)])
        w.j["textures"].append({"sampler": len(w.j["samplers"]) - 1, "source": len(w.j["images"]) - 1})
        m = json.loads(json.dumps(m))
        m["pbrMetallicRoughness"]["baseColorTexture"]["index"] = len(w.j["textures"]) - 1
        w.j["materials"].append(m)
        mat_of[mi] = len(w.j["materials"]) - 1
    for jn in joints:
        k = next(i for i, n in enumerate(skin) if g.name(n) == jn)
        W = g.world(skin[k])
        lin = W[:3, :3] @ (ROT_Z180 if flip_edge else np.eye(3))
        prims = []
        for nd in weapon.j["nodes"]:
            if "mesh" not in nd:
                continue
            for p in weapon.j["meshes"][nd["mesh"]]["primitives"]:
                a = p["attributes"]
                P = weapon.accessor(a["POSITION"]).astype(np.float64) @ lin.T + W[:3, 3]
                N = weapon.accessor(a["NORMAL"]).astype(np.float64) @ np.linalg.inv(lin)
                N /= np.linalg.norm(N, axis=1, keepdims=True).clip(1e-9)
                n = len(P)
                attrs = {
                    "POSITION": w.accessor(P.astype(np.float32), "VEC3", 5126, 34962),
                    "NORMAL": w.accessor(N.astype(np.float32), "VEC3", 5126, 34962),
                    "TEXCOORD_0": w.accessor(weapon.accessor(a["TEXCOORD_0"]).astype(np.float32), "VEC2", 5126, 34962),
                    "JOINTS_0": w.accessor(np.tile(np.array([k, 0, 0, 0], np.uint16), (n, 1)), "VEC4", 5123, 34962),
                    "WEIGHTS_0": w.accessor(np.tile(np.array([1, 0, 0, 0], np.float32), (n, 1)), "VEC4", 5126, 34962),
                }
                if "COLOR_0" in a:
                    attrs["COLOR_0"] = w.accessor(weapon.accessor(a["COLOR_0"]).astype(np.float32), "VEC4", 5126, 34962)
                idx = (weapon.accessor(p["indices"]) if "indices" in p else np.arange(n)).astype(np.uint32)
                prims.append({"attributes": attrs, "indices": w.accessor(idx, "SCALAR", 5125, 34963),
                              "material": mat_of[p.get("material", 0)]})
        w.j["meshes"].append({"name": f"weapon_{jn}", "primitives": prims})
        w.j["nodes"].append({"name": f"weapon_{jn}", "mesh": len(w.j["meshes"]) - 1, "skin": 0})
        w.j["scenes"][w.j.get("scene", 0)]["nodes"].append(len(w.j["nodes"]) - 1)
    return w


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("glb", type=Path)
    ap.add_argument("weapon", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--joints", default="lWeapIH,rWeapIH")
    ap.add_argument("--flip-edge", action="store_true")
    a = ap.parse_args()
    add_weapon(Glb(a.glb), Glb(a.weapon), a.joints.split(","), a.flip_edge).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
