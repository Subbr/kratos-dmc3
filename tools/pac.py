"""PAC/PNST do DMC3 HD: unpack/repack. Formato em docs/formats/pac.md.

Cabeçalho: magic (4) + count (u32 LE) + count offsets (u32 LE, 0 = item vazio).
Cada item vai do seu offset até o próximo offset não nulo (ou fim do arquivo), padding incluído.
Alinhamento dos itens: 16 bytes na maioria; 8 em 139 dos 3725 arquivos (detectado por arquivo).

Uso:
  python -I tools/pac.py unpack <arquivo.pac> <pasta>
  python -I tools/pac.py repack <pasta> <arquivo.pac>
"""
from __future__ import annotations

import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAGICS = (b"PAC\0", b"PNST")


@dataclass
class Pac:
    magic: bytes
    entries: list[bytes | None] = field(default_factory=list)  # None = slot vazio (offset 0)
    header_pad: int = 0  # bytes entre o fim da tabela e o primeiro item
    align: int = 16
    pad_bytes: bytes = b""  # conteúdo desse intervalo quando não é zero (msg_eng.pac do Crimson tem 0x20 ali, T38)

    @classmethod
    def parse(cls, data: bytes) -> "Pac":
        magic = data[:4]
        if magic not in MAGICS:
            raise ValueError(f"magic desconhecido: {magic!r}")
        (count,) = struct.unpack_from("<I", data, 4)
        offsets = struct.unpack_from(f"<{count}I", data, 8)
        used = sorted(o for o in offsets if o)
        if any(a >= b for a, b in zip(used, used[1:])) or (used and used[-1] > len(data)):
            raise ValueError("offsets fora de ordem ou além do fim do arquivo")
        end_of = {o: e for o, e in zip(used, used[1:] + [len(data)])}
        entries = [data[o:end_of[o]] if o else None for o in offsets]
        header_end = 8 + 4 * count
        header_pad = (used[0] - header_end) if used else len(data) - header_end
        align = 8 if any(len(e) % 16 for e in entries if e is not None) else 16
        pad = data[header_end:header_end + header_pad]
        return cls(magic, entries, header_pad, align, pad if any(pad) else b"")

    def build(self) -> bytes:
        count = len(self.entries)
        header_end = 8 + 4 * count
        pos = header_end + self.header_pad
        offsets, body = [], bytearray()
        for entry in self.entries:
            if entry is None:
                offsets.append(0)
                continue
            offsets.append(pos)
            padded = entry + b"\0" * (-len(entry) % self.align)
            body += padded
            pos += len(padded)
        head = self.magic + struct.pack(f"<I{count}I", count, *offsets)
        pad = self.pad_bytes if len(self.pad_bytes) == self.header_pad else b"\0" * self.header_pad
        return head + pad + bytes(body)


def unpack(src: Path, dst: Path) -> None:
    pac = Pac.parse(src.read_bytes())
    dst.mkdir(parents=True, exist_ok=True)
    index = []
    for i, entry in enumerate(pac.entries):
        if entry is None:
            index.append(None)
            continue
        name = f"{i:03d}.{entry[:4].rstrip(bytes(1)).decode('ascii', 'replace').strip() or 'bin'}"
        name = "".join(c if c.isalnum() or c in "._" else "_" for c in name)
        (dst / name).write_bytes(entry)
        index.append(name)
    meta = {"magic": pac.magic.decode("latin-1"), "header_pad": pac.header_pad, "align": pac.align,
            "entries": index}
    if pac.pad_bytes:
        meta["pad_bytes"] = pac.pad_bytes.hex()
    (dst / "pac.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")


def repack(src: Path, dst: Path) -> None:
    meta = json.loads((src / "pac.json").read_text(encoding="utf-8"))
    entries = [None if n is None else (src / n).read_bytes() for n in meta["entries"]]
    pad = bytes.fromhex(meta.get("pad_bytes", ""))
    dst.write_bytes(Pac(meta["magic"].encode("latin-1"), entries, meta["header_pad"], meta["align"], pad).build())


if __name__ == "__main__":
    cmd, a, b = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    {"unpack": unpack, "repack": repack}[cmd](a, b)
