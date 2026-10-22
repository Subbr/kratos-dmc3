"""Gera os pl000_00_N.pac com as animações do Kratos a partir de mapping/motions.yaml.

Uso: python -I tools/build_motions.py <pasta com os pl000_00_N.pac originais> <pasta de saída> [--blades <pl000.pac>]
--blades: o modelo tem ossos de lâmina (24/25); todas as motions do jogador ganham as trilhas deles
(blade_chain.py), com alcance da corrente nos golpes do grupo da arma das Blades (pl000_00_3).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_retarget as ar  # noqa: E402
import blade_chain  # noqa: E402
import kratos_fit  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


REACH_PACS = {"pl000_00_3", "pl000_00_13", "demo_pl000_00_3"}  # Rebellion (Blades) e Swordmaster da Rebellion


def main(src: Path, dst: Path, blades: Path | None = None) -> None:
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
    if blades:
        model = mod.Model.parse(pac.Pac.parse(blades.read_bytes()).entries[1])
        offsets = blade_chain.blade_offsets(model)
        _, parent = kratos_fit.dante_joints(body)
        for f in sorted(src.glob("*pl000_00_*.pac")):
            out = dst / f.name
            p = pac.Pac.parse((out if out.exists() else f).read_bytes())
            n = 0
            for i, e in enumerate(p.entries):
                if e is None or e[4:8] != b"MOT\0":
                    continue
                m = mot.Motion.parse(e)
                if m.bone_count != 24:
                    continue
                blade_chain.add_blade_tracks(m, offsets, body, parent, reach=f.stem in REACH_PACS)
                p.entries[i] = m.build(pad=True)
                n += 1
            out.write_bytes(p.build())
            print(f"{f.name}: {n} motions com ossos de lâmina")

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--blades", type=Path)
    a = ap.parse_args()
    main(a.src, a.dst, a.blades)
