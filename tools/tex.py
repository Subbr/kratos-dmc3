"""Bloco de texturas dos PACs do DMC3 HD (ex.: item 000 do pl000.pac). Formato em docs/formats/tex.md.

[u32 count][u32 setores × count] padding até 0x800; cada textura ocupa setores × 0x800 bytes:
8 bytes zero + descritor de 0x68 bytes + DDS (cabeçalho de 128 bytes + dados), padding com zeros.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

SECTOR = 0x800
DESC_OFF, DDS_OFF = 0x08, 0x70


def _sectors(n: int) -> int:
    return (n + SECTOR - 1) // SECTOR


@dataclass
class Texture:
    descriptor: bytes  # 0x68 bytes
    dds: bytes         # arquivo DDS completo ("DDS " + 124 + dados)
    sectors: int       # tamanho alocado em setores (pode sobrar espaço)
    trailer: bytes = b""  # bytes não nulos após o DDS dentro do espaço alocado (só nos id440*)

    @property
    def size(self) -> tuple[int, int]:
        return struct.unpack_from("<HH", self.descriptor, 8)


@dataclass
class TextureBlock:
    textures: list[Texture]

    @staticmethod
    def looks_like(b: bytes) -> bool:
        if len(b) < SECTOR or len(b) % SECTOR:
            return False
        (n,) = struct.unpack_from("<I", b, 0)
        if not 0 < n < 0x1F0:
            return False
        secs = struct.unpack_from(f"<{n}I", b, 4)
        return SECTOR + SECTOR * sum(secs) == len(b) and b[SECTOR + DDS_OFF:SECTOR + DDS_OFF + 4] == b"DDS "

    @classmethod
    def parse(cls, b: bytes) -> "TextureBlock":
        if not cls.looks_like(b):
            raise ValueError("não é bloco de texturas")
        (n,) = struct.unpack_from("<I", b, 0)
        textures, pos = [], SECTOR
        for secs in struct.unpack_from(f"<{n}I", b, 4):
            chunk = b[pos:pos + secs * SECTOR]
            (payload,) = struct.unpack_from("<I", chunk, DESC_OFF + 0x30)
            end = DDS_OFF + 128 + payload
            trailer = chunk[end:] if any(chunk[end:]) else b""
            textures.append(Texture(chunk[DESC_OFF:DDS_OFF], chunk[DDS_OFF:end], secs, trailer))
            pos += secs * SECTOR
        return cls(textures)

    def build(self) -> bytes:
        head = struct.pack(f"<I{len(self.textures)}I", len(self.textures), *(t.sectors for t in self.textures))
        out = bytearray(head + bytes(SECTOR - len(head)))
        for t in self.textures:
            chunk = bytes(DESC_OFF) + t.descriptor + t.dds + t.trailer
            out += chunk + bytes(t.sectors * SECTOR - len(chunk))
        return bytes(out)


def make_texture(dds: bytes, template: bytes) -> Texture:
    """Cria uma textura a partir de um DDS, copiando o descritor de outra e ajustando os campos conhecidos
    (relações confirmadas em docs/formats/tex.md)."""
    if dds[:4] != b"DDS ":
        raise ValueError("não é DDS")
    h, w = struct.unpack_from("<II", dds, 12)
    mips = max(1, struct.unpack_from("<I", dds, 28)[0])
    payload = len(dds) - 128
    d = bytearray(template)
    d[1] = mips  # byte 0 = flags (0x88 no jogo, 0x00 no Crimson): mantém o do modelo
    struct.pack_into("<HH", d, 0x08, w, h)
    struct.pack_into("<I", d, 0x30, payload)
    struct.pack_into("<HH", d, 0x3C, w // 2, h // 2)
    struct.pack_into("<ff", d, 0x40, 2 / w, 2 / h)
    struct.pack_into("<I", d, 0x5C, payload + 128)
    return Texture(bytes(d), dds, _sectors(DDS_OFF + len(dds)))
