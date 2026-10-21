"""Gera os pl000_00_N.pac com as animações do Kratos a partir de mapping/motions.yaml.

Uso: python -I tools/build_motions.py <pasta com os pl000_00_N.pac originais> <pasta de saída>
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_retarget as ar  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(src: Path, dst: Path) -> None:
    table = yaml.safe_load((ROOT / "mapping" / "motions.yaml").read_text(encoding="utf-8"))
    cfg = yaml.safe_load((ROOT / "mapping" / "skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
    g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
    body = mod.Model.parse((ROOT / "extracted/dmc3/unpacked/pl000/001.MOD").read_bytes())
    dst.mkdir(parents=True, exist_ok=True)
    for name, entries in table.items():
        p = pac.Pac.parse((src / f"{name}.pac").read_bytes())
        for idx, e in entries.items():
            base = mot.Motion.parse(p.entries[idx])
            frames = int(round(base.frames)) + 1
            new = ar.retarget(g, e["anim"], body, cfg, frames, base, e.get("timing", "stretch"))
            p.entries[idx] = new.build(pad=True)
            print(f"{name} #{idx}: {e['anim']} ({frames} frames, {e.get('timing', 'stretch')})")
        (dst / f"{name}.pac").write_bytes(p.build())


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
