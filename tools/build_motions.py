"""Gera os pl000_00_N.pac com as animações do Kratos a partir de mapping/motions.yaml.

Uso: python -I tools/build_motions.py <pasta com os pl000_00_N.pac originais> <pasta de saída> [--model <pl000.pac>]
--model: modelo com lâminas nos ossos 23/4; todas as motions do jogador (*pl000_00_*.pac) vão para esse
esqueleto e ganham as trilhas das lâminas (blade_chain.py), com alcance nos golpes do grupo das Blades.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np
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
# Blade of Artemis (Agni & Rudra e o Swordmaster dela): as Blades of Chaos somem (escala ~0 nos ossos 23/4; T73)
HIDE_BLADES = {"pl000_00_5", "pl000_00_15"}


def main(src: Path, dst: Path, model: Path | None = None) -> None:
    """model: pl000.pac do Kratos com lâminas nos ossos 23/4 (kratos_fit --blade-bones). Sem ele, só as motions
    da tabela são trocadas, no esqueleto do Dante."""
    table = yaml.safe_load((ROOT / "mapping" / "motions.yaml").read_text(encoding="utf-8"))
    cfg = yaml.safe_load((ROOT / "mapping" / "skeleton_kratos_dante.yaml").read_text(encoding="utf-8"))
    g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
    if model:
        body = mod.Model.parse(pac.Pac.parse(model.read_bytes()).entries[1])
        cfg = kratos_fit.blade_cfg(cfg)
        offsets = blade_chain.blade_offsets(body)
        dante = mod.Model.parse((ROOT / "extracted/dmc3/unpacked/pl000/001.MOD").read_bytes())
        neck_off, head_off = (np.array(struct.unpack_from("<3f", dante.skeleton.transforms[b])) for b in (4, 5))
    else:
        body = mod.Model.parse((ROOT / "extracted/dmc3/unpacked/pl000/001.MOD").read_bytes())
    _, parent = kratos_fit.dante_joints(body)
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*pl000_00_*.pac")) if model else [src / f"{n}.pac" for n in table]
    for f in files:
        name = f.stem
        p = pac.Pac.parse(f.read_bytes())
        kratos = table.get(name, {})
        n = 0
        for idx, e in enumerate(p.entries):
            if e is None or e[4:8] != b"MOT\0":
                continue
            m = mot.Motion.parse(e)
            if m.bone_count != 24:
                continue
            if idx in kratos:
                k = kratos[idx]
                frames = int(round(m.frames)) + 1
                m = ar.retarget(g, k["anim"], body, cfg, frames, m, k.get("timing", "stretch"), k.get("loop", False))
                print(f"{name} #{idx}: {k['anim']} ({frames} frames, {k.get('timing', 'stretch')})")
            elif model:
                blade_chain.fold_neck_into_head(m, neck_off, head_off)
            else:
                continue
            if model:
                blade_chain.add_blade_tracks(m, offsets, body, parent, reach=name in REACH_PACS)
                # escala explícita em toda motion: sem trilha o osso guarda o valor da motion anterior (como na translação)
                scale = 0.001 if name in HIDE_BLADES else 1.0
                for b in offsets:
                    for ch in ("sx", "sy", "sz"):
                        m.tracks.append(mot.Track.hermite(b, ch, [scale] * (int(round(m.frames)) + 1)))
            p.entries[idx] = m.build(pad=True)
            n += 1
        (dst / f.name).write_bytes(p.build())
        print(f"{f.name}: {n} motions")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--model", type=Path, help="pl000.pac com lâminas nos ossos 23/4")
    a = ap.parse_args()
    main(a.src, a.dst, a.model)
