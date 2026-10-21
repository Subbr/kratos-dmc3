"""MOD (modelo do DMC3 HD): leitura e escrita. Formato em docs/formats/mod.md.

A escrita reconstrói o arquivo do zero (recalcula todos os offsets); o round-trip
byte a byte em todos os MODs do jogo valida as regras de layout.
Base de campos: DMC3-Blender-Import-Addon (MIT), DMC3/model.py e common/meshutils.py.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

HEADER_SIZE = 0x40
OBJECT_SIZE = 0x40
MESH_SIZE = 0x50


def _align(n: int, a: int = 16) -> int:
    return (n + a - 1) // a * a


@dataclass
class Mesh:
    tex: int
    pad: bytes                 # 12 bytes após vertCount/tex (zeros nos arquivos vistos)
    reserved: tuple[int, int, int]  # 3 × i64 após os 5 offsets: zero, uk (offset obsoleto?), zero
    positions: list[tuple[float, float, float]]
    normals: list[tuple[float, float, float]]
    uvs: list[tuple[int, int]]          # s16, escala 1/4096
    bones: list[bytes]                  # 4 bytes/vértice: [?, b0*4, b1*4, b2*4]
    weights: list[int]                  # u16: 3×5 bits de peso + bit 15 = reinício da strip

    @property
    def vert_count(self) -> int:
        return len(self.positions)


@dataclass
class Object:
    ukn: int                   # byte após meshCount (128 no Dante)
    pad: bytes                 # 4 bytes após numVerts
    flags: int
    rest: bytes                # 28 bytes após flags
    bsphere: tuple[float, float, float, float]
    meshes: list[Mesh] = field(default_factory=list)
    num_verts: int | None = None  # valor gravado; None = soma das malhas (no pl000 do Crimson não bate)


@dataclass
class Skeleton:
    parents: bytes             # hierarchy
    order: bytes               # hierarchyOrder
    children: bytes            # childIdx
    transforms: list[bytes]    # 32 bytes por osso (3 floats de posição + 0x14 bytes)
    head_pad: bytes            # bytes entre os 4 offsets e o primeiro array


@dataclass
class Model:
    magic: bytes
    version: float
    header: bytes              # bytes 0x08..0x40 com contagens e offset do esqueleto zerados
    objects: list[Object]
    skeleton: Skeleton | None
    tail: bytes                # área de trabalho após o esqueleto (ver runtime_tail)
    bone_count: int = 0
    # Bytes exatos entre o fim da seção anterior e cada seção, na ordem de escrita.
    # None = só zeros de alinhamento (o normal). Conteúdo só em 12 modelos de menu e nos MODs do Crimson.
    gaps: list[bytes | None] = field(default_factory=list)

    # ---------------------------------------------------------------- leitura
    @classmethod
    def parse(cls, b: bytes) -> "Model":
        magic = b[:4]
        if magic != b"MOD ":
            raise ValueError(f"não é MOD: {magic!r}")
        (version,) = struct.unpack_from("<f", b, 4)
        obj_count, bone_count = b[0x10], b[0x11]
        (skel_off,) = struct.unpack_from("<q", b, 0x20)
        header = bytearray(b[8:HEADER_SIZE])
        header[0x10 - 8] = header[0x11 - 8] = 0
        header[0x20 - 8:0x28 - 8] = bytes(8)
        objects, data_end = [], HEADER_SIZE + obj_count * OBJECT_SIZE
        for i in range(obj_count):
            o = HEADER_SIZE + i * OBJECT_SIZE
            mesh_count, ukn = b[o], b[o + 1]
            (num_verts,) = struct.unpack_from("<h", b, o + 2)
            pad = b[o + 4:o + 8]
            (mesh_off,) = struct.unpack_from("<q", b, o + 8)
            (flags,) = struct.unpack_from("<I", b, o + 16)
            obj = Object(ukn, pad, flags, b[o + 20:o + 48], struct.unpack_from("<4f", b, o + 48), num_verts=num_verts)
            for m in range(mesh_count):
                mo = mesh_off + m * MESH_SIZE
                vc, tex = struct.unpack_from("<hh", b, mo)
                p, n, uv, bi, w, r0, r1, r2 = struct.unpack_from("<8q", b, mo + 16)
                obj.meshes.append(Mesh(
                    tex, b[mo + 4:mo + 16], (r0, r1, r2),
                    [struct.unpack_from("<3f", b, p + 12 * k) for k in range(vc)],
                    [struct.unpack_from("<3f", b, n + 12 * k) for k in range(vc)],
                    [struct.unpack_from("<2h", b, uv + 4 * k) for k in range(vc)],
                    [b[bi + 4 * k:bi + 4 * k + 4] for k in range(vc)],
                    list(struct.unpack_from(f"<{vc}H", b, w)),
                ))
                data_end = max(data_end, w + 2 * vc)
            objects.append(obj)
        skeleton, tail_start = None, data_end
        if skel_off:
            hier, order, child, trans = struct.unpack_from("<4i", b, skel_off)
            bc = bone_count
            skeleton = Skeleton(
                b[skel_off + hier:skel_off + hier + bc], b[skel_off + order:skel_off + order + bc],
                b[skel_off + child:skel_off + child + bc],
                [b[skel_off + trans + 32 * k:skel_off + trans + 32 * k + 32] for k in range(bc)],
                b[skel_off + 16:skel_off + hier],
            )
            skeleton_layout = cls._skeleton_offsets(bc, len(skeleton.head_pad))
            if skeleton_layout != (hier, order, child, trans):
                raise ValueError(f"layout de esqueleto inesperado: {(hier, order, child, trans)}")
            tail_start = skel_off + trans + 32 * bc
        model = cls(magic, version, bytes(header), objects, skeleton, b[tail_start:], bone_count)
        model.gaps = model._gaps_from(b)
        return model

    def _sections(self, b: bytes) -> list[tuple[int, int]]:
        """(offset, tamanho) de cada seção no arquivo, na ordem em que build() escreve."""
        out = []
        for i, obj in enumerate(self.objects):
            o = HEADER_SIZE + i * OBJECT_SIZE
            (mesh_off,) = struct.unpack_from("<q", b, o + 8)
            out.append((mesh_off, MESH_SIZE * len(obj.meshes)))
            sizes = (12, 12, 4, 4, 2)
            for col, size in enumerate(sizes):
                for m, mesh in enumerate(obj.meshes):
                    (off,) = struct.unpack_from("<q", b, mesh_off + m * MESH_SIZE + 16 + 8 * col)
                    out.append((off, size * mesh.vert_count))
        if self.skeleton:
            (skel_off,) = struct.unpack_from("<q", b, 0x20)
            out.append((skel_off, 0))
        return out

    def _gaps_from(self, b: bytes) -> list[bytes | None]:
        gaps: list[bytes | None] = []
        pos = HEADER_SIZE + OBJECT_SIZE * len(self.objects)
        for off, size in self._sections(b):
            if off < pos:
                raise ValueError(f"seções sobrepostas em {off:#x}")
            raw = b[pos:off]
            gaps.append(None if raw == bytes(_align(pos) - pos) else raw)
            pos = off + size
        return gaps

    @staticmethod
    def _skeleton_offsets(bc: int, head_pad: int) -> tuple[int, int, int, int]:
        hier = 16 + head_pad
        order = _align(hier + bc, 4)
        child = _align(order + bc, 4)
        trans = _align(child + bc)
        return hier, order, child, trans

    def runtime_tail(self, fill: int = 0x12) -> bytes:
        """Área que o jogo usa para converter as strips em índices: Σ align16(6 × (vértices − 2)) por malha.
        Regra confirmada em 6474/6474 MODs; sem ela o jogo trava ao carregar o modelo (T3)."""
        size = sum(_align(6 * max(m.vert_count - 2, 0)) for o in self.objects for m in o.meshes)
        return bytes([fill]) * size

    # ---------------------------------------------------------------- escrita
    def build(self) -> bytes:
        out = bytearray(HEADER_SIZE + OBJECT_SIZE * len(self.objects))
        out[:4] = self.magic
        struct.pack_into("<f", out, 4, self.version)
        out[8:HEADER_SIZE] = self.header
        out[0x10], out[0x11] = len(self.objects), self.bone_count

        gaps = iter(self.gaps)

        def put(blob: bytes) -> int:
            gap = next(gaps, None)
            out.extend(bytes(_align(len(out)) - len(out)) if gap is None else gap)
            pos = len(out)
            out.extend(blob)
            return pos

        for i, obj in enumerate(self.objects):
            o = HEADER_SIZE + i * OBJECT_SIZE
            mesh_off = put(bytes(MESH_SIZE * len(obj.meshes)))
            # dados agrupados por atributo: posições de todas as malhas, depois normais, UVs, ossos, pesos
            encoders = (
                lambda m: b"".join(struct.pack("<3f", *v) for v in m.positions),
                lambda m: b"".join(struct.pack("<3f", *v) for v in m.normals),
                lambda m: b"".join(struct.pack("<2h", *v) for v in m.uvs),
                lambda m: b"".join(m.bones),
                lambda m: struct.pack(f"<{m.vert_count}H", *m.weights),
            )
            offsets = [[put(enc(mesh)) for mesh in obj.meshes] for enc in encoders]
            for m, mesh in enumerate(obj.meshes):
                mo = mesh_off + m * MESH_SIZE
                struct.pack_into("<hh", out, mo, mesh.vert_count, mesh.tex)
                out[mo + 4:mo + 16] = mesh.pad
                struct.pack_into("<8q", out, mo + 16, *(col[m] for col in offsets), *mesh.reserved)
            out[o], out[o + 1] = len(obj.meshes), obj.ukn
            num_verts = obj.num_verts if obj.num_verts is not None else sum(m.vert_count for m in obj.meshes)
            struct.pack_into("<h", out, o + 2, num_verts)
            out[o + 4:o + 8] = obj.pad
            struct.pack_into("<qI", out, o + 8, mesh_off, obj.flags)
            out[o + 20:o + 48] = obj.rest
            struct.pack_into("<4f", out, o + 48, *obj.bsphere)
        if self.skeleton:
            s, bc = self.skeleton, self.bone_count
            hier, order, child, trans = self._skeleton_offsets(bc, len(s.head_pad))
            blob = bytearray(trans + 32 * bc)
            struct.pack_into("<4i", blob, 0, hier, order, child, trans)
            blob[16:hier] = s.head_pad
            blob[hier:hier + bc], blob[order:order + bc], blob[child:child + bc] = s.parents, s.order, s.children
            blob[trans:] = b"".join(s.transforms)
            skel_off = put(bytes(blob))
            struct.pack_into("<q", out, 0x20, skel_off)
        out.extend(self.tail)
        return bytes(out)
