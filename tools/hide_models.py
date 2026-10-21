"""Esconde todos os MODs de um PAC (nenhum vértice fecha triângulo); o resto do arquivo fica intacto.
Uso: python -I tools/hide_models.py <entrada.pac> <saida.pac>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
import pac  # noqa: E402


def hide(data: bytes) -> tuple[bytes, int]:
    p = pac.Pac.parse(data)
    count = 0
    for i, e in enumerate(p.entries):
        if e is None:
            continue
        if e[:4] == b"MOD ":
            m = mod.Model.parse(e)
            for o in m.objects:
                for me in o.meshes:
                    me.weights = [w | 0x8000 for w in me.weights]
            p.entries[i] = m.build()
            count += 1
        elif e[:4] in pac.MAGICS:
            p.entries[i], n = hide(e)
            count += n
    return p.build(), count


if __name__ == "__main__":
    out, n = hide(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_bytes(out)
    print(f"{sys.argv[2]}: {n} modelos escondidos")
