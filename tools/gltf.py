"""Leitura mínima de .glb (glTF 2.0 binário): nós, hierarquia, skin, malhas. Sem dependências além de numpy."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

_COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


class Glb:
    def __init__(self, path: Path):
        b = Path(path).read_bytes()
        (jlen,) = struct.unpack_from("<I", b, 12)
        self.j = json.loads(b[20:20 + jlen])
        self.bin = b[20 + jlen + 8:]
        self.parent = {c: i for i, n in enumerate(self.j["nodes"]) for c in n.get("children", [])}

    def accessor(self, idx: int) -> np.ndarray:
        a = self.j["accessors"][idx]
        bv = self.j["bufferViews"][a["bufferView"]]
        dt, nc = _COMP[a["componentType"]], _NCOMP[a["type"]]
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = bv.get("byteStride", 0)
        item = np.dtype(dt).itemsize * nc
        if stride and stride != item:
            raw = np.frombuffer(self.bin, np.uint8, a["count"] * stride, start).reshape(-1, stride)[:, :item]
            arr = np.frombuffer(raw.tobytes(), dt)
        else:
            arr = np.frombuffer(self.bin, dt, a["count"] * nc, start)
        arr = arr.reshape(a["count"], nc) if nc > 1 else arr
        if a.get("normalized") and dt != np.float32:
            arr = arr.astype(np.float32) / np.iinfo(dt).max
        return arr

    def local(self, i: int) -> np.ndarray:
        n = self.j["nodes"][i]
        if "matrix" in n:
            return np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T
        x, y, z, w = n.get("rotation", [0, 0, 0, 1])
        r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        m = np.eye(4)
        m[:3, :3] = r * np.array(n.get("scale", [1, 1, 1]))
        m[:3, 3] = n.get("translation", [0, 0, 0])
        return m

    def world(self, i: int) -> np.ndarray:
        m = self.local(i)
        while i in self.parent:
            i = self.parent[i]
            m = self.local(i) @ m
        return m

    def name(self, i: int) -> str:
        return self.j["nodes"][i].get("name", f"node{i}")
