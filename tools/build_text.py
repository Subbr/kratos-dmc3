"""Textos de interface/loja do DMC3 com os nomes do GoW1 (Fase 8): msg_eng.pac do .nbz do usuário → override.

Uso: python -I tools/build_text.py <msg_eng.pac original> <saída msg_eng.pac>
Troca bytes (os comentários do arquivo estão em Shift-JIS) e reempacota com tools/pac.py (round-trip idêntico, T38).
Diálogos da história (mNN_*_msg_*) ficam para a Fase 9.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pac  # noqa: E402

REPLACE = [(b"Devil Trigger", b"Rage of the Gods"), (b"Dante", b"Kratos")]


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "msg"
        pac.unpack(src, d)
        for f in d.iterdir():
            if f.name == "pac.json":
                continue
            data = f.read_bytes()
            for a, b in REPLACE:
                print(f"{f.name}: {a.decode()} x{data.count(a)}")
                data = data.replace(a, b)
            f.write_bytes(data)
        dst.parent.mkdir(parents=True, exist_ok=True)
        pac.repack(d, dst)


if __name__ == "__main__":
    main()
