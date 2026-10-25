"""Gera o arquivo de golpes do motor Kratos (D11) a partir do grafo de combate do próprio GoW1.

Uso: python -I tools/build_engine_moves.py <pl000_00_2.pac base> <pl000.pac do Kratos> <saída kratosMoves_pl000_00_2.pac>
Grafo: TWK_CombatFile_000…006 (tools/gow_combat.py). Configuração em mapping/engine_moves.yaml. Saída extra:
KratosMoves.json (índice, quadros, quadro do golpe, próximo □/△ e ponto de corte, ficha de dano) para a DLL.
As animações do GoW1 são "no lugar" (a raiz `main` não se move): o avanço vai no osso 0 (`forward`).
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anim_retarget as ar  # noqa: E402
import blade_chain  # noqa: E402
import gow_combat  # noqa: E402
import kratos_fit  # noqa: E402
import mod  # noqa: E402
import mot  # noqa: E402
import pac  # noqa: E402
from gltf import Glb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def transition(move: dict, trigger: int) -> tuple[int, float] | None:
    """(destino, ponto de corte) da transição de solo do gatilho: a de máscara com bit 0 (executa) dá o corte."""
    best = None
    for t in move["trans"]:
        if t["trigger"] != trigger or t["target"] < 0 or t["diff"] > 0:
            continue
        if t["mask"] & 1:
            return t["target"], t["window"][0]
        best = best or (t["target"], t["window"][1])
    return best


def main(base_pac: Path, model: Path, out: Path) -> None:
    conf = yaml.safe_load((ROOT / "mapping/engine_moves.yaml").read_text(encoding="utf-8"))
    graph = {m["id"]: m for m in gow_combat.load_all(gow_combat.load_hashes())}
    g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
    anims = {a["name"].split(" ")[-1].upper(): a["name"].split(" ")[-1] for a in g.j["animations"]}
    light, heavy = conf["triggers"]["light"], conf["triggers"]["heavy"]
    # fecho a partir das raízes, só golpes com animação no glb
    order, kind, todo = [], {}, list(conf["roots"])
    for r in conf["roots"]:
        kind[r] = "light"
    while todo:
        mid = todo.pop(0)
        if mid in order or mid not in graph or graph[mid]["anim"] not in anims:
            continue
        if any(graph[mid]["anim"].startswith(x) for x in conf.get("exclude_prefix", [])):
            continue
        order.append(mid)
        for trig, k in ((light, "light"), (heavy, "heavy")):
            tr = transition(graph[mid], trig)
            if tr and tr[0] not in kind:
                kind[tr[0]] = k
                todo.append(tr[0])
    cfg = kratos_fit.blade_cfg(yaml.safe_load((ROOT / "mapping/skeleton_kratos_dante.yaml").read_text(encoding="utf-8")))
    body = mod.Model.parse(pac.Pac.parse(model.read_bytes()).entries[1])
    _, parent = kratos_fit.dante_joints(body)
    offsets = blade_chain.blade_offsets(body)
    p = pac.Pac.parse(base_pac.read_bytes())
    template = mot.Motion.parse(next(e for e in p.entries if e and e[4:8] == b"MOT\0"))
    struct.pack_into("<f", template.header, 0x08, 0.0)  # play_start (cópia em 0x10): toca desde o 1º quadro
    struct.pack_into("<f", template.header, 0x10, 0.0)
    index = {mid: k for k, mid in enumerate(order)}
    entries, info = [], []
    for mid in order:
        mv = graph[mid]
        name = anims[mv["anim"]]
        anim = ar.KratosAnim(g, name)
        frames = max(int(anim.duration * 60) + 1, 2)
        base = mot.Motion(bytearray(template.header))
        base.frames = float(frames - 1)
        fwd = float(conf["forward"].get(kind[mid], conf["forward"]["default"]))
        base.tracks = [mot.Track.linear(ar.ROOT_MOTION_BONE, c, [0.0] * frames) for c in ("tx", "ty")]
        base.tracks.append(mot.Track.linear(ar.ROOT_MOTION_BONE, "tz",
                           [fwd * min(1.0, f / max(1, 0.4 * (frames - 1))) for f in range(frames)]))
        m = ar.retarget(g, name, body, cfg, frames, base, "natural")
        hit = ar.strike_frame(m, body, parent, frames)
        blade_chain.add_blade_tracks(m, offsets, body, parent, reach=True)
        for b in offsets:
            for ch in ("sx", "sy", "sz"):
                m.tracks.append(mot.Track.hermite(b, ch, [1.0] * frames))
        entries.append(m.build(pad=True))
        nl, nh = transition(mv, light), transition(mv, heavy)
        dmg = conf["damage"].get(mv["anim"], conf["damage"][kind[mid]] if kind[mid] in conf["damage"] else conf["damage"]["default"])
        info.append({"name": mv["anim"], "gowId": mid, "frames": frames, "hitFrame": hit,
                     "next": index.get(nl[0], -1) if nl else -1, "nextCut": nl[1] if nl else 1.0,
                     "nextHeavy": index.get(nh[0], -1) if nh else -1, "heavyCut": nh[1] if nh else 1.0,
                     "damage": str(dmg)})
        print(f"#{index[mid]} {mv['anim']} (id {mid}, {frames} quadros, golpe {hit}) □→{info[-1]['next']}@{info[-1]['nextCut']} "
              f"△→{info[-1]['nextHeavy']}@{info[-1]['heavyCut']} dano {dmg}")
    p.entries = entries
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(p.build())
    # um arquivo por golpe, com a motion no índice 0: o jogo trata os índices do grupo TAUNTS (0–3 no Dante) e
    # travou ao tocar o índice 6 (T85); a DLL troca o arquivo do grupo a cada golpe
    for k, e in enumerate(entries):
        single = pac.Pac.parse(base_pac.read_bytes())
        single.entries = [e]
        (out.parent / f"kratosMove{k:02d}_pl000_00_2.pac").write_bytes(single.build())
    (out.parent / "KratosMoves.json").write_text(json.dumps({"moves": info}, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
