"""Exporta o MOD de um PAC (ou arquivo .MOD) para OBJ, para inspeção visual. Uso: mod_to_obj.py <pac|MOD> <saida.obj> [item]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
import pac  # noqa: E402

src, out = Path(sys.argv[1]), Path(sys.argv[2])
data = src.read_bytes()
if data[:4] in pac.MAGICS:
    data = pac.Pac.parse(data).entries[int(sys.argv[3]) if len(sys.argv) > 3 else 1]
m = mod.Model.parse(data)
lines, base = [], 1
for oi, o in enumerate(m.objects):
    for mi, me in enumerate(o.meshes):
        lines.append(f"o obj{oi}_m{mi}_tex{me.tex}")
        lines += [f"v {x:.4f} {y:.4f} {z:.4f}" for x, y, z in me.positions]
        for i in range(2, me.vert_count):
            if not me.weights[i] >> 15:
                lines.append(f"f {base + i - 2} {base + i - 1} {base + i}")
        base += me.vert_count
out.write_text("\n".join(lines) + "\n")
print(out, base - 1, "vértices")
