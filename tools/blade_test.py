"""T14: motion de parada com 26 ossos; a lâmina direita (osso 24) sai da mão ao longo do braço e volta.

Uso: python -I tools/blade_test.py <pl000_00_0.pac de entrada> <saida.pac> <pl000.pac com ossos de lâmina>
"""
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402

src, dst, model = (Path(x) for x in sys.argv[1:4])
body = mod.Model.parse(pac.Pac.parse(model.read_bytes()).entries[1])
off24 = np.array(struct.unpack_from("<3f", body.skeleton.transforms[24]))
off25 = np.array(struct.unpack_from("<3f", body.skeleton.transforms[25]))
p = pac.Pac.parse(src.read_bytes())
for idx in (0,):  # parada
    m = mot.Motion.parse(p.entries[idx])
    n = int(round(m.frames)) + 1
    m.resize_bones(body.bone_count)
    ext = [80.0 * np.sin(np.pi * f / (n - 1)) ** 2 for f in range(n)]  # 0 -> 80 -> 0
    for bone, off, side in ((24, off24, -1.0), (25, off25, 1.0)):
        # braço direito do Dante aponta para -x na pose de repouso; o esquerdo para +x
        m.tracks.append(mot.Track.hermite(bone, "tx", [off[0] + side * e for e in ext]))
        m.tracks.append(mot.Track.hermite(bone, "ty", [off[1]] * n))
        m.tracks.append(mot.Track.hermite(bone, "tz", [off[2]] * n))
    p.entries[idx] = m.build(pad=True)
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(p.build())
print(dst)
