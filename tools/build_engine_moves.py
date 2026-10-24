"""Gera o arquivo de golpes do motor Kratos (D11): as animações do GoW1 no tempo original, para a DLL tocar.

Uso: python -I tools/build_engine_moves.py <pl000_00_2.pac base> <pl000.pac do Kratos> <saída kratosMoves_pl000_00_2.pac>
Tabela em mapping/engine_moves.yaml. As animações do GoW1 são "no lugar" (a raiz `main` não se move): o avanço do
golpe vai no osso 0 (deslocamento do ator, como nas motions do Dante) a partir de `forward`.
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


def main(base_pac: Path, model: Path, out: Path) -> None:
    table = yaml.safe_load((ROOT / "mapping/engine_moves.yaml").read_text(encoding="utf-8"))["moves"]
    cfg = kratos_fit.blade_cfg(yaml.safe_load((ROOT / "mapping/skeleton_kratos_dante.yaml").read_text(encoding="utf-8")))
    g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
    body = mod.Model.parse(pac.Pac.parse(model.read_bytes()).entries[1])
    _, parent = kratos_fit.dante_joints(body)
    offsets = blade_chain.blade_offsets(body)
    p = pac.Pac.parse(base_pac.read_bytes())
    template = mot.Motion.parse(next(e for e in p.entries if e and e[4:8] == b"MOT\0"))
    import struct
    struct.pack_into("<f", template.header, 0x08, 0.0)  # play_start (cópia em 0x10): toca desde o 1º quadro
    struct.pack_into("<f", template.header, 0x10, 0.0)
    entries = []
    info = []
    for k, mv in enumerate(table):
        anim = ar.KratosAnim(g, mv["anim"])
        frames = max(int(anim.duration * 60) + 1, 2)
        base = mot.Motion(bytearray(template.header))
        base.frames = float(frames - 1)
        base.tracks = [mot.Track.linear(ar.ROOT_MOTION_BONE, c, [0.0] * frames) for c in ("tx", "ty")]
        # avanço: sobe nos primeiros 40% do golpe e fica (o GoW1 dá o passo junto com o corte) [HIPÓTESE]
        fwd = float(mv.get("forward", 0))
        base.tracks.append(mot.Track.linear(ar.ROOT_MOTION_BONE, "tz",
                           [fwd * min(1.0, f / max(1, 0.4 * (frames - 1))) for f in range(frames)]))
        m = ar.retarget(g, mv["anim"], body, cfg, frames, base, "natural", mv.get("loop", False))
        hit = ar.strike_frame(m, body, parent, frames)
        blade_chain.add_blade_tracks(m, offsets, body, parent, reach=True)
        for b in offsets:
            for ch in ("sx", "sy", "sz"):
                m.tracks.append(mot.Track.hermite(b, ch, [1.0] * frames))
        entries.append(m.build(pad=True))
        info.append({"name": mv["name"], "frames": frames, "hitFrame": hit, "next": mv.get("next", -1),
                     "nextHeavy": mv.get("nextHeavy", -1), "damage": mv.get("damage", "5C68C0"),
                     "window": mv.get("window", [0.15, 0.75])})
        print(f"#{k} {mv['name']}: {mv['anim']} ({frames} quadros, golpe no {hit}, avanço {fwd})")
    p.entries = entries
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(p.build())
    # tabela para a DLL (Crimson\\configs\\KratosMoves.json): índice, quadros, quadro do golpe, cadeia e dano
    import json
    (out.parent / "KratosMoves.json").write_text(json.dumps({"moves": info}, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
