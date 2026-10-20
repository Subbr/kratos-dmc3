"""Inventário do dmc3-0.nbz (ZIP com GData.afs/). Somente leitura.

Uso: python -I tools/nbz_inventory.py [saida.csv]
"""
from __future__ import annotations

import csv
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

PREFIX = "GData.afs/"


def classify(name: str) -> str:
    n = name.lower()
    rules = [
        ("pl000_00_", "dante_motion"), ("pl000", "dante"), ("plwp_", "arma_jogador"),
        ("pl0", "jogador_outro"), ("em", "inimigo"), ("st", "cenario"), ("id", "interface"),
        ("snd_", "som"), ("demo_", "demo"), ("m_", "mensagens"),
    ]
    for prefix, kind in rules:
        if n.startswith(prefix):
            return kind
    return "outro"


def main() -> None:
    nbz = paths.get("DMC3_NBZ")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else paths.ROOT / "extracted" / "dmc3" / "inventory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with zipfile.ZipFile(nbz) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.removeprefix(PREFIX)
            with z.open(info) as f:
                magic = f.read(4)
            rows.append({
                "nome": name,
                "tamanho": info.file_size,
                "comprimido": info.compress_size,
                "crc32": f"{info.CRC:08X}",
                "magic": magic.hex(),
                "magic_ascii": "".join(chr(b) if 32 <= b < 127 else "." for b in magic),
                "tipo": classify(name),
            })
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} arquivos -> {out}")
    print("por tipo:", Counter(r["tipo"] for r in rows).most_common())
    print("magic por extensão:")
    by_ext: dict[str, Counter] = {}
    for r in rows:
        by_ext.setdefault(r["nome"].rsplit(".", 1)[-1], Counter())[r["magic_ascii"]] += 1
    for ext, c in sorted(by_ext.items()):
        print(f"  .{ext}: {c.most_common(4)}")


if __name__ == "__main__":
    main()
