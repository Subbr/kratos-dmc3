"""Decodifica o TWK_CombatFile do GoW1 (D11): golpes e seus eventos (janela, condição, ação, alvo).

Uso: python -I tools/gow_combat.py <CombatFile_NNN.json do gowb> [--move N]
Layout pela função do executável que interpreta os eventos (FUN_00205488, docs/formats/gow-combat.md):
golpe (24 bytes a partir de 0x08): +0 hash da animação, +4 id, +6/+8/+10 listas (relativas ao golpe), +0x16 nº de eventos;
lista A3 (+10): n × (u16 deslocamento relativo à própria entrada, u16 índice) → evento:
+8 início e +10 fim da janela (fração da animação × 65535), +0xC alvo (s16), +0xE chance %, +0xF ação, +0x10 condição,
+0x11 dificuldade mínima, +0x12 flags.
"""
from __future__ import annotations

import base64
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_hashes() -> dict[int, str]:
    hd = {}
    for line in (ROOT / "vendor/god_of_war_browser/hashes.dump.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split(":", 2)
        if len(p) == 3 and not line.startswith("#"):
            try:
                hd[int(p[0], 16)] = p[2]
            except ValueError:
                pass
    return hd


def blob(path: Path) -> bytes:
    d = json.loads(path.read_text())["Data"]["Tree"]

    def find(n):
        if n.get("Fields"):
            for f in n["Fields"]:
                r = find(f)
                if r:
                    return r
        elif n.get("Value"):
            return n["Value"]
    return base64.b64decode(find(d))


def decode(b: bytes, hd: dict[int, str]) -> list[dict]:
    n = struct.unpack_from("<H", b, 0)[0]
    moves = []
    for i in range(n):
        o = 8 + i * 24
        h, mid, a1, a2, a3 = struct.unpack_from("<IHHHH", b, o)
        nev = b[o + 0x16]
        evs = []
        for k in range(nev):
            e = o + a3 + k * 4
            off = struct.unpack_from("<H", b, e)[0]
            r = e + off
            start, end = struct.unpack_from("<HH", b, r + 8)
            target = struct.unpack_from("<h", b, r + 0xC)[0]
            chance, action, cond, diff, flags = b[r + 0xE], b[r + 0xF], b[r + 0x10], b[r + 0x11], b[r + 0x12]
            evs.append({"window": (round(start / 65535, 3), round(end / 65535, 3)), "cond": cond, "action": action,
                        "target": target, "chance": chance, "diff": diff, "flags": flags,
                        "raw": b[r:r + 0x14].hex()})
        moves.append({"index": i, "id": mid, "anim": hd.get(h, hex(h)), "events": evs,
                      "fields": struct.unpack_from("<6H", b, o + 12)})
    return moves


def main() -> None:
    hd = load_hashes()
    moves = decode(blob(Path(sys.argv[1])), hd)
    only = int(sys.argv[sys.argv.index("--move") + 1]) if "--move" in sys.argv else None
    byid = {m["id"]: m["anim"] for m in moves}
    for m in moves:
        if only is not None and m["index"] != only:
            continue
        print(f"#{m['index']} id={m['id']} {m['anim']} campos={m['fields']} eventos={len(m['events'])}")
        for e in m["events"]:
            tgt = byid.get(e["target"], "")
            print(f"    janela {e['window']} cond {e['cond']} ação {e['action']:3d} alvo {e['target']:4d} {tgt:16s} "
                  f"chance {e['chance']} dif {e['diff']} flags {e['flags']:#x}")


if __name__ == "__main__":
    main()
