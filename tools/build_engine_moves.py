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


def zero_root(g: Glb, anim: ar.KratosAnim, frames: int, scale: float) -> tuple[list[float], list[float]] | None:
    """Deslocamento do GoW1 no chão: a junta `zeroJoint` do glb (fora da hierarquia do quadril) leva a translação do
    golpe (evadeFront −146 em z, dash −82, combo3A −24; T89). Osso 0 = (posição − posição inicial) × escala, girada
    180° em Y como o resto do esqueleto (kratos_fit.ROT_Y180)."""
    node = next((i for i, n in enumerate(g.j["nodes"]) if n.get("name") == "zeroJoint"), None)
    if node is None:
        return None
    p0 = anim._value(node, "translation", 0.0, [0, 0, 0])[:3]
    xs, zs = [], []
    for f in range(frames):
        d = (anim._value(node, "translation", min(f / 60.0, anim.duration), [0, 0, 0])[:3] - p0) * scale
        v = kratos_fit.ROT_Y180[:3, :3] @ d
        xs.append(float(v[0]))
        zs.append(float(v[2]))
    return xs, zs


def main(base_pac: Path, model: Path, out: Path) -> None:
    conf = yaml.safe_load((ROOT / "mapping/engine_moves.yaml").read_text(encoding="utf-8"))
    graph = {m["id"]: m for m in gow_combat.load_all(gow_combat.load_hashes())}
    g = Glb(ROOT / "extracted/gow1/hero0/hero_obj.glb")
    anims = {a["name"].split(" ")[-1].upper(): a["name"].split(" ")[-1] for a in g.j["animations"]}
    anims.update({k: v for k, v in conf.get("anim_alias", {}).items() if v.upper() in anims})
    light, heavy = conf["triggers"]["light"], conf["triggers"]["heavy"]
    # fecho a partir das raízes, só golpes com animação no glb
    evades = conf.get("evades", {})
    order, kind, todo = [], {}, list(conf["roots"]) + list(evades.values())
    for r in conf["roots"]:
        kind[r] = "light"
    for r in evades.values():
        kind[r] = "evade"
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
    spells, end_next = {}, {}
    stop = set(conf.get("spell_chain_stop", []))
    for sname, mid in conf.get("spells", {}).items():
        if mid not in graph or graph[mid]["anim"] not in anims:
            continue
        spells[sname] = mid
        cur = mid
        while cur is not None:  # sequência do GoW1: segue o gatilho "fim da animação" (0x0b)
            if cur not in order:
                order.append(cur)
                kind[cur] = "spell"
            nxt = next((t["target"] for t in graph[cur]["trans"] if t["trigger"] == 0x0B and t["target"] >= 0
                        and t["target"] != cur and t["target"] in graph and graph[t["target"]]["anim"] not in stop
                        and graph[t["target"]]["anim"] in anims and t["target"] not in end_next.values()
                        and t["target"] != mid), None)
            if nxt is not None:
                end_next[cur] = nxt
            cur = nxt
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
        # o retarget só escreve rotação nos ossos que têm trilha de rotação na base (anim_retarget.py): sem elas o
        # corpo ficava na pose de repouso (Kratos em T no jogo, 2026-10-25)
        base.tracks = [t for t in template.tracks if t.bone != ar.ROOT_MOTION_BONE and t.channel[0] == "r"]
        # deslocamento no osso 0: golpes avançam `forward` em 40% da animação; esquivas andam `root` [x, z] em
        # `root_span` da animação (as animações do GoW1 são "no lugar")
        root = zero_root(g, anim, frames, float(cfg["scale"]))
        if root is None:  # sem zeroJoint: avanço provisório
            rx, rz = conf.get("root", {}).get(graph[mid]["anim"], [0.0, fwd])
            span = conf.get("root_span", {}).get(kind[mid], 0.4)
            ramp = [min(1.0, f / max(1, span * (frames - 1))) for f in range(frames)]
            root = ([rx * r for r in ramp], [rz * r for r in ramp])
        base.tracks += [mot.Track.linear(ar.ROOT_MOTION_BONE, "tx", root[0]),
                        mot.Track.linear(ar.ROOT_MOTION_BONE, "ty", [0.0] * frames),
                        mot.Track.linear(ar.ROOT_MOTION_BONE, "tz", root[1])]
        m = ar.retarget(g, name, body, cfg, frames, base, "natural")
        hit = ar.strike_frame(m, body, parent, frames)
        if mv["anim"] in conf.get("spell_hit", {}):
            hit = int(frames * conf["spell_hit"][mv["anim"]])
        blade_chain.add_blade_tracks(m, offsets, body, parent, reach=kind[mid] not in ("spell", "evade"))  # magia: lâminas na mão
        for b in offsets:
            for ch in ("sx", "sy", "sz"):
                m.tracks.append(mot.Track.hermite(b, ch, [1.0] * frames))
        entries.append(m.build(pad=True))
        nl, nh = transition(mv, light), transition(mv, heavy)
        dmg = conf["damage"].get(mv["anim"], conf["damage"][kind[mid]] if kind[mid] in conf["damage"] else conf["damage"]["default"])
        info.append({"name": mv["anim"], "gowId": mid, "frames": frames, "hitFrame": hit,
                     "next": index.get(nl[0], -1) if nl else -1, "nextCut": nl[1] if nl else 1.0,
                     "nextHeavy": index.get(nh[0], -1) if nh else -1, "heavyCut": nh[1] if nh else 1.0,
                     "damage": str(dmg), "nextEnd": index.get(end_next.get(mid), -1),
                     "spell": conf.get("spell_fx", {}).get(mv["anim"], ""), "kind": kind[mid]})
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
    spell_index = {n: index[m] for n, m in spells.items()}
    evade_index = {n: index[m] for n, m in evades.items() if m in index}
    (out.parent / "KratosMoves.json").write_text(json.dumps({"moves": info, "spells": spell_index, "evades": evade_index}, indent=1),
                                                 encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
